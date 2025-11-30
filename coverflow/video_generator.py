"""Video generation for coverflow effect."""

import sys
import threading
from typing import Callable, List, Optional

import cv2
import numpy as np

from .config import Config
from .renderer import CoverflowRenderer
from .utils import ease_in_out_cubic


class VideoGenerator:
    """Generates coverflow video from images."""

    def __init__(self, config: Config):
        """Initialize the video generator.

        Args:
            config: Video generation configuration.
        """
        self.config = config
        self.renderer = CoverflowRenderer(config)

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
        total_duration = total_frames / self.config.fps

        # Statistics mode: just print stats and return
        if self.config.statistics:
            print("Statistics:")
            print(f"  Images: {num_images}")
            print(f"  Total frames: {total_frames}")
            print(f"  Duration: {total_duration:.2f} seconds")
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
                offset = ease_in_out_cubic(offset)

            # Render and save
            canvas = self.renderer.render_frame(images, img_idx, offset)
            cv2.imwrite("preview.jpg", canvas)
            print(f"Preview saved to 'preview.jpg' (frame {target_frame}, image {img_idx + 1}/{num_images})")
            return

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            self.config.output,
            fourcc,
            self.config.fps,
            (self.config.width, self.config.height),
        )

        if not out.isOpened():
            print(f"Error: Could not create video file '{self.config.output}'")
            sys.exit(1)

        frame_count = 0

        print("Generating video...")

        for img_idx in range(num_images):
            # Check for cancellation
            if cancel_flag and cancel_flag.is_set():
                out.release()
                print("Video generation cancelled.")
                return

            # Hold phase - keep current image centered
            print(f"  Processing image {img_idx + 1}/{num_images} - hold phase")
            for frame in range(hold_frames):
                # Check for cancellation
                if cancel_flag and cancel_flag.is_set():
                    out.release()
                    print("Video generation cancelled.")
                    return

                canvas = self.renderer.render_frame(images, img_idx, 0)
                out.write(canvas)
                frame_count += 1

                # Report progress
                if progress_callback:
                    progress_callback(frame_count, total_frames)

            # Transition phase - animate to next image
            if img_idx < num_images - 1:
                print(f"  Processing image {img_idx + 1}/{num_images} - transition phase")
                for frame in range(transition_frames):
                    # Check for cancellation
                    if cancel_flag and cancel_flag.is_set():
                        out.release()
                        print("Video generation cancelled.")
                        return

                    # Calculate offset (0 to 1)
                    offset = frame / transition_frames
                    # Use easing function for smooth animation
                    offset = ease_in_out_cubic(offset)

                    canvas = self.renderer.render_frame(images, img_idx, offset)
                    out.write(canvas)
                    frame_count += 1

                    # Report progress
                    if progress_callback:
                        progress_callback(frame_count, total_frames)

        out.release()
        print(f"Video saved to '{self.config.output}' ({frame_count} frames)")
