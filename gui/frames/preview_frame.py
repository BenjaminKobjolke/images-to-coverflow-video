"""Preview display frame."""

from typing import Callable, Optional
import customtkinter as ctk
from PIL import Image
import numpy as np
import cv2


class PreviewFrame(ctk.CTkFrame):
    """Frame for displaying preview images."""

    def __init__(
        self,
        master,
        on_refresh: Optional[Callable[[], None]] = None,
        on_frame_change: Optional[Callable[[int], None]] = None,
        **kwargs
    ):
        """Initialize the preview frame.

        Args:
            master: Parent widget.
            on_refresh: Callback when refresh button is clicked.
            on_frame_change: Callback when frame slider changes.
        """
        super().__init__(master, **kwargs)

        self.on_refresh = on_refresh
        self.on_frame_change = on_frame_change
        self._current_image = None
        self._total_frames = 100

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Preview canvas (CTkLabel with image)
        self.preview_label = ctk.CTkLabel(
            self,
            text="No preview\n\nSelect a source folder and click Refresh",
            width=640,
            height=480,
        )
        self.preview_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Controls frame
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        controls_frame.grid_columnconfigure(1, weight=1)

        # Frame label
        ctk.CTkLabel(controls_frame, text="Frame:").grid(row=0, column=0, padx=(0, 10))

        # Frame slider
        self.frame_slider = ctk.CTkSlider(
            controls_frame,
            from_=0,
            to=100,
            command=self._on_slider_change,
        )
        self.frame_slider.set(0)
        self.frame_slider.grid(row=0, column=1, padx=5, sticky="ew")

        # Frame value label
        self.frame_label = ctk.CTkLabel(controls_frame, text="0 / 100", width=80)
        self.frame_label.grid(row=0, column=2, padx=10)

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            controls_frame,
            text="Refresh",
            width=80,
            command=self._on_refresh_click,
        )
        self.refresh_btn.grid(row=0, column=3)

    def _on_slider_change(self, value: float):
        """Handle frame slider change."""
        frame = int(value)
        self.frame_label.configure(text=f"{frame} / {self._total_frames}")
        if self.on_frame_change:
            self.on_frame_change(frame)

    def _on_refresh_click(self):
        """Handle refresh button click."""
        if self.on_refresh:
            self.on_refresh()

    def set_total_frames(self, total: int):
        """Set the total number of frames for the slider."""
        self._total_frames = max(1, total)
        self.frame_slider.configure(to=self._total_frames - 1)
        current = int(self.frame_slider.get())
        self.frame_label.configure(text=f"{current} / {self._total_frames}")

    def get_frame_number(self) -> int:
        """Get the currently selected frame number."""
        return int(self.frame_slider.get())

    def set_frame_number(self, frame: int):
        """Set the current frame number."""
        self.frame_slider.set(frame)
        self.frame_label.configure(text=f"{frame} / {self._total_frames}")

    def display_image(self, cv_image: np.ndarray):
        """Display an OpenCV image in the preview area.

        Args:
            cv_image: OpenCV image (BGR format).
        """
        # Convert BGR to RGB
        rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

        # Convert to PIL
        pil_image = Image.fromarray(rgb)

        # Scale to fit preview area while maintaining aspect ratio
        preview_width = self.preview_label.winfo_width()
        preview_height = self.preview_label.winfo_height()

        # Use minimum sensible size if widget not yet rendered
        if preview_width < 100:
            preview_width = 640
        if preview_height < 100:
            preview_height = 480

        # Calculate scale to fit
        scale = min(
            preview_width / pil_image.width,
            preview_height / pil_image.height,
        )
        new_width = int(pil_image.width * scale)
        new_height = int(pil_image.height * scale)

        pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

        # Convert to CTkImage
        ctk_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(new_width, new_height),
        )

        self.preview_label.configure(image=ctk_image, text="")
        self._current_image = ctk_image  # Keep reference to prevent garbage collection

    def set_loading(self, loading: bool = True):
        """Show loading state."""
        if loading:
            self.preview_label.configure(text="Loading preview...")
            self.refresh_btn.configure(state="disabled")
        else:
            self.refresh_btn.configure(state="normal")

    def show_error(self, message: str):
        """Show an error message in the preview area."""
        self.preview_label.configure(image=None, text=message)
        self._current_image = None
