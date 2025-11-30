"""Background worker for video generation."""

import threading
from typing import Callable, Optional

from coverflow import Config, ImageLoader, VideoGenerator


class VideoWorker:
    """Worker for generating video in the background."""

    def __init__(
        self,
        config: Config,
        on_progress: Callable[[int, int], None],
        on_complete: Callable[[bool, Optional[str]], None],
    ):
        """Initialize the video worker.

        Args:
            config: Video generation configuration.
            on_progress: Callback with (current_frame, total_frames).
            on_complete: Callback with (success, error_message).
        """
        self.config = config
        self.on_progress = on_progress
        self.on_complete = on_complete
        self._cancel_flag = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start video generation in background thread."""
        self._cancel_flag.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def cancel(self):
        """Request cancellation of video generation."""
        self._cancel_flag.set()

    def is_running(self) -> bool:
        """Check if the worker is still running."""
        return self._thread is not None and self._thread.is_alive()

    def _run(self):
        """Worker thread main function."""
        try:
            # Load images
            loader = ImageLoader(self.config.source)
            images = loader.load_images()

            if not images:
                self.on_complete(False, "No images found in source folder")
                return

            # Generate video
            generator = VideoGenerator(self.config)
            generator.generate(
                images,
                progress_callback=self._progress_callback,
                cancel_flag=self._cancel_flag,
            )

            if self._cancel_flag.is_set():
                self.on_complete(False, "Cancelled by user")
            else:
                self.on_complete(True, None)

        except Exception as e:
            self.on_complete(False, str(e))

    def _progress_callback(self, current: int, total: int):
        """Called from generator for progress updates."""
        self.on_progress(current, total)
