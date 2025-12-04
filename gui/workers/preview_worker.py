"""Background worker for preview rendering."""

import threading
from typing import Callable, List, Optional
import numpy as np

from coverflow import Config, ImageLoader
from coverflow.renderer import CoverflowRenderer
from coverflow.utils import get_easing_function


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

            # Create renderer and get easing function
            renderer = CoverflowRenderer(self.config)
            easing_func = get_easing_function(self.config.easing)

            # Calculate which image and offset for this frame
            transition_frames = int(self.config.transition * self.config.fps)
            hold_frames = int(self.config.hold * self.config.fps)
            first_hold_frames = int((self.config.first_hold if self.config.first_hold is not None else self.config.hold) * self.config.fps)
            num_images = len(images)

            # Calculate total frames (must match calculate_total_frames)
            if num_images > 1:
                total_frames = first_hold_frames + (num_images - 1) * hold_frames + (num_images - 1) * transition_frames
            else:
                total_frames = first_hold_frames
            if self.config.loop:
                total_frames += transition_frames

            # Clamp frame number
            frame = max(0, min(self.frame_number, total_frames - 1))

            # Calculate the frame count without loop transition
            if num_images > 1:
                regular_frames = first_hold_frames + (num_images - 1) * hold_frames + (num_images - 1) * transition_frames
            else:
                regular_frames = first_hold_frames

            # Check if we're in the loop transition phase
            if self.config.loop and frame >= regular_frames:
                # Loop transition: last image transitioning back to first
                img_idx = num_images - 1
                trans_frame = frame - regular_frames
                offset = trans_frame / transition_frames if transition_frames > 0 else 0
                offset = easing_func(offset)
                in_transition = True
            else:
                # Normal playback: find which image and offset
                # First image segment has different hold duration
                first_segment = first_hold_frames + transition_frames
                regular_segment = hold_frames + transition_frames

                if frame < first_segment:
                    # We're in the first image segment
                    img_idx = 0
                    frame_in_segment = frame
                    current_hold_frames = first_hold_frames
                else:
                    # We're past the first segment
                    remaining = frame - first_segment
                    img_idx = 1 + remaining // regular_segment
                    frame_in_segment = remaining % regular_segment
                    current_hold_frames = hold_frames

                # Clamp image index
                img_idx = min(img_idx, num_images - 1)

                if frame_in_segment < current_hold_frames:
                    offset = 0  # In hold phase
                    in_transition = False
                else:
                    # In transition phase
                    trans_frame = frame_in_segment - current_hold_frames
                    offset = trans_frame / transition_frames if transition_frames > 0 else 0
                    offset = easing_func(offset)
                    in_transition = True

            # Render frame with optional motion blur
            motion_blur = self.config.motion_blur
            step_size = 1.0 / transition_frames if transition_frames > 0 else 0

            if motion_blur > 0 and in_transition:
                # Render multiple sub-frames and blend for motion blur
                accumulated = None
                for i in range(motion_blur):
                    sub_offset = offset + (i / motion_blur) * step_size
                    sub_offset = min(sub_offset, 1.0)
                    sub_frame = renderer.render_frame(images, img_idx, sub_offset)
                    if accumulated is None:
                        accumulated = sub_frame.astype(np.float32)
                    else:
                        accumulated += sub_frame.astype(np.float32)
                canvas = (accumulated / motion_blur).astype(np.uint8)
            else:
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
    first_hold_frames = int((config.first_hold if config.first_hold is not None else config.hold) * config.fps)
    # First image may have different hold duration
    if num_images > 1:
        total = first_hold_frames + (num_images - 1) * hold_frames + (num_images - 1) * transition_frames
    else:
        total = first_hold_frames
    # Add extra transition for loop (last to first)
    if config.loop:
        total += transition_frames
    return total
