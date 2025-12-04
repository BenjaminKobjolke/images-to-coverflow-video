"""Video generation for coverflow effect."""

import sys
import threading
from typing import Callable, List, Optional

import cv2
import imageio
import numpy as np

from .config import Config
from .renderer import CoverflowRenderer
from .utils import get_easing_function


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
        num_images = len(images)

        # Calculate total frames: hold for each image + transitions between images
        total_frames = num_images * hold_frames + (num_images - 1) * transition_frames
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
            frames_per_image = hold_frames + transition_frames
            img_idx = target_frame // frames_per_image
            frame_in_segment = target_frame % frames_per_image

            # Clamp image index
            img_idx = min(img_idx, num_images - 1)

            if frame_in_segment < hold_frames:
                offset = 0  # In hold phase
            else:
                # In transition phase
                trans_frame = frame_in_segment - hold_frames
                offset = trans_frame / transition_frames if transition_frames > 0 else 0
                offset = self.easing_func(offset)

            # Render and save
            canvas = self.renderer.render_frame(images, img_idx, offset)
            cv2.imwrite("preview.jpg", canvas)
            print(f"Preview saved to 'preview.jpg' (frame {target_frame}, image {img_idx + 1}/{num_images})")
            return

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

        absolute_frame = 0  # Track position in full video
        frames_written = 0  # Track actually written frames
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
                out.close()
                print("Video generation cancelled.")
                return

            # Hold phase - keep current image centered
            print(f"  Processing image {img_idx + 1}/{num_images} - hold phase")
            for frame in range(hold_frames):
                # Check for cancellation
                if cancel_flag and cancel_flag.is_set():
                    out.close()
                    print("Video generation cancelled.")
                    return

                # Only write frames within the specified range
                if start_frame <= absolute_frame <= end_frame:
                    canvas = self.renderer.render_frame(images, img_idx, 0)
                    out.append_data(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
                    frames_written += 1

                    # Report progress based on frames to render
                    if progress_callback:
                        progress_callback(frames_written, frames_to_render)

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
                for frame in range(transition_frames):
                    # Check for cancellation
                    if cancel_flag and cancel_flag.is_set():
                        out.close()
                        print("Video generation cancelled.")
                        return

                    # Only write frames within the specified range
                    if start_frame <= absolute_frame <= end_frame:
                        # Calculate offset (0 to 1)
                        offset = frame / transition_frames
                        # Use easing function for smooth animation
                        offset = self.easing_func(offset)

                        canvas = self.renderer.render_frame(images, img_idx, offset)
                        out.append_data(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
                        frames_written += 1

                        # Report progress
                        if progress_callback:
                            progress_callback(frames_written, frames_to_render)

                    absolute_frame += 1

                    # Stop if we've passed the end frame
                    if absolute_frame > end_frame:
                        generation_complete = True
                        break

        # Loop transition - animate from last image back to first
        if self.config.loop and not generation_complete:
            print(f"  Processing loop transition (back to image 1)")
            for frame in range(transition_frames):
                # Check for cancellation
                if cancel_flag and cancel_flag.is_set():
                    out.close()
                    print("Video generation cancelled.")
                    return

                # Only write frames within the specified range
                if start_frame <= absolute_frame <= end_frame:
                    # Calculate offset (0 to 1)
                    offset = frame / transition_frames
                    # Use easing function for smooth animation
                    offset = self.easing_func(offset)

                    canvas = self.renderer.render_frame(images, num_images - 1, offset)
                    out.append_data(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
                    frames_written += 1

                    # Report progress
                    if progress_callback:
                        progress_callback(frames_written, frames_to_render)

                absolute_frame += 1

                # Stop if we've passed the end frame
                if absolute_frame > end_frame:
                    break

        out.close()
        print(f"Video saved to '{self.config.output}' ({frames_written} frames)")
