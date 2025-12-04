"""Video generation for coverflow effect."""

import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from threading import Thread, Event
from typing import Callable, List, Optional

import cv2
import imageio
import numpy as np

from .config import Config
from .renderer import CoverflowRenderer
from .utils import get_easing_function


class FrameBuffer:
    """Thread-safe frame buffer for render/encode pipeline.

    Separates rendering and encoding into different threads for smoother
    CPU utilization and better FFmpeg buffer management.
    """

    def __init__(self, max_size: int = 30):
        """Initialize the frame buffer.

        Args:
            max_size: Maximum number of frames to buffer (~1 second at 30fps).
        """
        self.queue: Queue = Queue(maxsize=max_size)
        self.done = Event()
        self.error: Optional[Exception] = None


class VideoGenerator:
    """Generates coverflow video from images."""

    def __init__(self, config: Config):
        """Initialize the video generator.

        Args:
            config: Video generation configuration.
        """
        self.config = config
        self.renderer = CoverflowRenderer(config)
        self.easing_func = get_easing_function(config.easing)

    def _render_with_motion_blur(
        self,
        images: List[np.ndarray],
        img_idx: int,
        base_offset: float,
        step_size: float,
    ) -> np.ndarray:
        """Render a frame with motion blur by blending multiple sub-frames.

        Uses parallel processing for >= 3 samples (thread pool overhead not worth it
        for fewer samples). The perspective cache in transforms.py is thread-safe.

        Args:
            images: List of images.
            img_idx: Current center image index.
            base_offset: Base offset for this frame (0 to 1).
            step_size: Offset step between frames (1/transition_frames).

        Returns:
            Blended frame with motion blur.
        """
        num_samples = self.config.motion_blur

        if num_samples <= 0:
            # No motion blur, render single frame
            return self.renderer.render_frame(images, img_idx, base_offset)

        # Threshold for parallel processing (thread overhead not worth it for few samples)
        MIN_SAMPLES_FOR_PARALLEL = 3
        MAX_WORKERS = 4  # Diminishing returns beyond 4 threads

        def render_subframe(i: int) -> np.ndarray:
            """Render a single sub-frame at the given sample index."""
            sub_offset = min(base_offset + (i / num_samples) * step_size, 1.0)
            return self.renderer.render_frame(images, img_idx, sub_offset)

        if num_samples >= MIN_SAMPLES_FOR_PARALLEL:
            # Parallel rendering for better performance
            with ThreadPoolExecutor(max_workers=min(num_samples, MAX_WORKERS)) as executor:
                sub_frames = list(executor.map(render_subframe, range(num_samples)))

            # Stack and average
            accumulated = np.sum(sub_frames, axis=0, dtype=np.float32)
            return (accumulated / num_samples).astype(np.uint8)
        else:
            # Sequential fallback for few samples (avoids thread overhead)
            accumulated = np.zeros(
                (self.config.height, self.config.width, 3), dtype=np.float32
            )

            for i in range(num_samples):
                sub_frame = render_subframe(i)
                np.add(accumulated, sub_frame, out=accumulated, casting='unsafe')

            return (accumulated / num_samples).astype(np.uint8)

    def _encode_frames(
        self,
        buffer: FrameBuffer,
        writer,
        progress_callback: Optional[Callable[[int, int], None]],
        frames_to_render: int,
    ) -> None:
        """Encoder thread - reads frames from buffer and writes to video.

        Runs in a separate thread to allow rendering and encoding to happen
        concurrently, improving overall throughput.

        Args:
            buffer: Frame buffer to read from.
            writer: Video writer (imageio) to write frames to.
            progress_callback: Optional callback for progress updates.
            frames_to_render: Total number of frames for progress calculation.
        """
        frames_written = 0
        try:
            while True:
                # Check if we're done and buffer is empty
                if buffer.done.is_set() and buffer.queue.empty():
                    break

                try:
                    # Get frame with timeout to allow checking done flag
                    frame = buffer.queue.get(timeout=0.1)
                    writer.append_data(frame)
                    frames_written += 1

                    if progress_callback:
                        progress_callback(frames_written, frames_to_render)

                except Empty:
                    # No frame available, check if we should exit
                    continue

        except Exception as e:
            # Store error for main thread to handle
            buffer.error = e

    def generate(
        self,
        images: List[np.ndarray],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        cancel_flag: Optional[threading.Event] = None,
    ) -> None:
        """Generate the coverflow video.

        Args:
            images: List of images to include in the video.
            progress_callback: Optional callback for progress updates (current, total).
            cancel_flag: Optional threading event to signal cancellation.
        """
        # Calculate frame counts
        transition_frames = int(self.config.transition * self.config.fps)
        hold_frames = int(self.config.hold * self.config.fps)
        first_hold_frames = int((self.config.first_hold if self.config.first_hold is not None else self.config.hold) * self.config.fps)
        num_images = len(images)

        # Calculate total frames: hold for each image + transitions between images
        # First image may have different hold duration
        if num_images > 1:
            total_frames = first_hold_frames + (num_images - 1) * hold_frames + (num_images - 1) * transition_frames
        else:
            total_frames = first_hold_frames
        # Add extra transition for loop (last to first)
        if self.config.loop:
            total_frames += transition_frames
        total_duration = total_frames / self.config.fps

        # Calculate frame range for rendering
        start_frame = self.config.start_frame if self.config.start_frame is not None else 0
        end_frame = self.config.end_frame if self.config.end_frame is not None else total_frames - 1

        # Clamp values to valid range
        start_frame = max(0, min(start_frame, total_frames - 1))
        end_frame = max(start_frame, min(end_frame, total_frames - 1))

        frames_to_render = end_frame - start_frame + 1

        # Statistics mode: just print stats and return
        if self.config.statistics:
            print("Statistics:")
            print(f"  Images: {num_images}")
            print(f"  Total frames: {total_frames}")
            print(f"  Duration: {total_duration:.2f} seconds")
            if self.config.start_frame is not None or self.config.end_frame is not None:
                print(f"  Render range: {start_frame} - {end_frame} ({frames_to_render} frames)")
            return

        # Preview mode: render single frame as preview.jpg
        if self.config.preview is not None:
            # Determine frame number
            if self.config.preview == int(self.config.preview):
                # Whole number = frame number
                target_frame = int(self.config.preview)
            else:
                # Decimal = seconds, convert to frame
                target_frame = int(self.config.preview * self.config.fps)

            # Clamp to valid range
            target_frame = max(0, min(target_frame, total_frames - 1))

            # Find which image and offset for this frame
            # First image segment has different hold duration
            first_segment = first_hold_frames + transition_frames
            regular_segment = hold_frames + transition_frames

            if target_frame < first_segment:
                # We're in the first image segment
                img_idx = 0
                frame_in_segment = target_frame
                current_hold_frames = first_hold_frames
            else:
                # We're past the first segment
                remaining = target_frame - first_segment
                img_idx = 1 + remaining // regular_segment
                frame_in_segment = remaining % regular_segment
                current_hold_frames = hold_frames

            # Clamp image index
            img_idx = min(img_idx, num_images - 1)

            if frame_in_segment < current_hold_frames:
                offset = 0  # In hold phase
            else:
                # In transition phase
                trans_frame = frame_in_segment - current_hold_frames
                offset = trans_frame / transition_frames if transition_frames > 0 else 0
                offset = self.easing_func(offset)

            # Render and save
            canvas = self.renderer.render_frame(images, img_idx, offset)
            cv2.imwrite("preview.jpg", canvas)
            print(f"Preview saved to 'preview.jpg' (frame {target_frame}, image {img_idx + 1}/{num_images})")
            return

        # Pre-scale all images for faster rendering
        print("Preparing images...")
        self.renderer.prepare_images(images)

        # Build FFmpeg output parameters
        output_params = ['-preset', self.config.preset, '-crf', str(self.config.crf)]
        if self.config.max_bitrate:
            bitrate_val = str(self.config.max_bitrate)
            # Skip if value is 0 (no limit)
            try:
                if float(bitrate_val.rstrip('kKmM')) == 0:
                    bitrate_val = None
            except ValueError:
                pass
            if bitrate_val:
                # Append 'k' if no unit suffix (user entered raw number)
                if bitrate_val[-1].isdigit():
                    bitrate_val += 'k'
                output_params += ['-maxrate', bitrate_val, '-bufsize', bitrate_val]

        # Select codec based on encoder setting
        codec = 'libx264' if self.config.encoder == 'h264' else 'libx265'

        # Initialize imageio video writer
        try:
            out = imageio.get_writer(
                self.config.output,
                fps=self.config.fps,
                codec=codec,
                output_params=output_params
            )
        except Exception as e:
            print(f"Error: Could not create video file '{self.config.output}': {e}")
            sys.exit(1)

        # Create frame buffer for render/encode pipeline
        frame_buffer = FrameBuffer(max_size=30)

        # Start encoder thread
        encoder_thread = Thread(
            target=self._encode_frames,
            args=(frame_buffer, out, progress_callback, frames_to_render),
            daemon=True
        )
        encoder_thread.start()

        absolute_frame = 0  # Track position in full video
        generation_complete = False

        if start_frame > 0 or end_frame < total_frames - 1:
            print(f"Generating video (frames {start_frame} - {end_frame})...")
        else:
            print("Generating video...")

        for img_idx in range(num_images):
            if generation_complete:
                break

            # Check for cancellation
            if cancel_flag and cancel_flag.is_set():
                frame_buffer.done.set()
                encoder_thread.join(timeout=5.0)
                out.close()
                print("Video generation cancelled.")
                return

            # Hold phase - keep current image centered
            # First image uses first_hold_frames, rest use hold_frames
            current_hold_frames = first_hold_frames if img_idx == 0 else hold_frames
            print(f"  Processing image {img_idx + 1}/{num_images} - hold phase")

            # Cache the hold frame - render once, write multiple times
            hold_frame_rgb = None

            for frame in range(current_hold_frames):
                # Check for cancellation
                if cancel_flag and cancel_flag.is_set():
                    frame_buffer.done.set()
                    encoder_thread.join(timeout=5.0)
                    out.close()
                    print("Video generation cancelled.")
                    return

                # Only write frames within the specified range
                if start_frame <= absolute_frame <= end_frame:
                    # Render hold frame only once, then reuse
                    if hold_frame_rgb is None:
                        hold_frame_cache = self.renderer.render_frame(images, img_idx, 0)
                        hold_frame_rgb = cv2.cvtColor(hold_frame_cache, cv2.COLOR_BGR2RGB)

                    # Push frame to buffer (encoder thread handles writing)
                    frame_buffer.queue.put(hold_frame_rgb)

                absolute_frame += 1

                # Stop if we've passed the end frame
                if absolute_frame > end_frame:
                    generation_complete = True
                    break

            if generation_complete:
                break

            # Transition phase - animate to next image
            if img_idx < num_images - 1:
                print(f"  Processing image {img_idx + 1}/{num_images} - transition phase")
                step_size = 1.0 / transition_frames if transition_frames > 0 else 0
                for frame in range(transition_frames):
                    # Check for cancellation
                    if cancel_flag and cancel_flag.is_set():
                        frame_buffer.done.set()
                        encoder_thread.join(timeout=5.0)
                        out.close()
                        print("Video generation cancelled.")
                        return

                    # Only write frames within the specified range
                    if start_frame <= absolute_frame <= end_frame:
                        # Calculate offset (0 to 1)
                        offset = frame / transition_frames
                        # Use easing function for smooth animation
                        offset = self.easing_func(offset)

                        # Render with motion blur if enabled
                        canvas = self._render_with_motion_blur(images, img_idx, offset, step_size)
                        # Push frame to buffer (encoder thread handles writing)
                        frame_buffer.queue.put(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))

                    absolute_frame += 1

                    # Stop if we've passed the end frame
                    if absolute_frame > end_frame:
                        generation_complete = True
                        break

        # Loop transition - animate from last image back to first
        if self.config.loop and not generation_complete:
            print(f"  Processing loop transition (back to image 1)")
            step_size = 1.0 / transition_frames if transition_frames > 0 else 0
            for frame in range(transition_frames):
                # Check for cancellation
                if cancel_flag and cancel_flag.is_set():
                    frame_buffer.done.set()
                    encoder_thread.join(timeout=5.0)
                    out.close()
                    print("Video generation cancelled.")
                    return

                # Only write frames within the specified range
                if start_frame <= absolute_frame <= end_frame:
                    # Calculate offset (0 to 1)
                    offset = frame / transition_frames
                    # Use easing function for smooth animation
                    offset = self.easing_func(offset)

                    # Render with motion blur if enabled
                    canvas = self._render_with_motion_blur(images, num_images - 1, offset, step_size)
                    # Push frame to buffer (encoder thread handles writing)
                    frame_buffer.queue.put(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))

                absolute_frame += 1

                # Stop if we've passed the end frame
                if absolute_frame > end_frame:
                    break

        # Signal encoder thread that rendering is complete
        frame_buffer.done.set()
        encoder_thread.join(timeout=30.0)  # Wait for encoder to finish

        # Check for encoder errors
        if frame_buffer.error:
            print(f"Warning: Encoder error occurred: {frame_buffer.error}")

        out.close()
        print(f"Video saved to '{self.config.output}'")
