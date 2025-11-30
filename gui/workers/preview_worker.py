"""Background worker for preview rendering."""

import threading
from typing import Callable, List, Optional
import numpy as np

from coverflow import Config, ImageLoader
from coverflow.renderer import CoverflowRenderer
from coverflow.utils import ease_in_out_cubic


class PreviewWorker:
    """Worker for rendering preview frames in the background."""

    def __init__(
        self,
        config: Config,
        on_complete: Callable[[Optional[np.ndarray], Optional[str]], None],
        frame_number: int = 0,
    ):
        """Initialize the preview worker.

        Args:
            config: Video generation configuration.
            on_complete: Callback with (image, error_message).
            frame_number: Frame number to render.
        """
        self.config = config
        self.on_complete = on_complete
        self.frame_number = frame_number
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start preview rendering in background thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        """Worker thread main function."""
        try:
            # Load images
            loader = ImageLoader(self.config.source)
            images = loader.load_images()

            if not images:
                self.on_complete(None, "No images found in source folder")
                return

            # Create renderer
            renderer = CoverflowRenderer(self.config)

            # Calculate which image and offset for this frame
            transition_frames = int(self.config.transition * self.config.fps)
            hold_frames = int(self.config.hold * self.config.fps)
            num_images = len(images)
            total_frames = num_images * hold_frames + (num_images - 1) * transition_frames

            # Clamp frame number
            frame = max(0, min(self.frame_number, total_frames - 1))

            # Find which image and offset
            frames_per_image = hold_frames + transition_frames
            img_idx = frame // frames_per_image
            frame_in_segment = frame % frames_per_image

            # Clamp image index
            img_idx = min(img_idx, num_images - 1)

            if frame_in_segment < hold_frames:
                offset = 0  # In hold phase
            else:
                # In transition phase
                trans_frame = frame_in_segment - hold_frames
                offset = trans_frame / transition_frames if transition_frames > 0 else 0
                offset = ease_in_out_cubic(offset)

            # Render frame
            canvas = renderer.render_frame(images, img_idx, offset)
            self.on_complete(canvas, None)

        except Exception as e:
            self.on_complete(None, str(e))


def calculate_total_frames(config: Config, num_images: int) -> int:
    """Calculate total frames for a video.

    Args:
        config: Video configuration.
        num_images: Number of images.

    Returns:
        Total frame count.
    """
    transition_frames = int(config.transition * config.fps)
    hold_frames = int(config.hold * config.fps)
    total = num_images * hold_frames + (num_images - 1) * transition_frames
    # Add extra transition for loop (last to first)
    if config.loop:
        total += transition_frames
    return total
