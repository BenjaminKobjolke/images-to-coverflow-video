"""Video generation for coverflow effect."""

import sys
from typing import List

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
        self.renderer = CoverflowRenderer(config.width, config.height)

    def generate(self, images: List[np.ndarray]) -> None:
        """Generate the coverflow video.

        Args:
            images: List of images to include in the video.
        """
        # Calculate frame counts
        transition_frames = int(self.config.transition * self.config.fps)
        hold_frames = int(self.config.hold * self.config.fps)

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

        total_frames = 0
        num_images = len(images)

        print("Generating video...")

        for img_idx in range(num_images):
            # Hold phase - keep current image centered
            print(f"  Processing image {img_idx + 1}/{num_images} - hold phase")
            for frame in range(hold_frames):
                canvas = self.renderer.render_frame(images, img_idx, 0)
                out.write(canvas)
                total_frames += 1

            # Transition phase - animate to next image
            if img_idx < num_images - 1:
                print(f"  Processing image {img_idx + 1}/{num_images} - transition phase")
                for frame in range(transition_frames):
                    # Calculate offset (0 to 1)
                    offset = frame / transition_frames
                    # Use easing function for smooth animation
                    offset = ease_in_out_cubic(offset)

                    canvas = self.renderer.render_frame(images, img_idx, offset)
                    out.write(canvas)
                    total_frames += 1

        out.release()
        print(f"Video saved to '{self.config.output}' ({total_frames} frames)")
