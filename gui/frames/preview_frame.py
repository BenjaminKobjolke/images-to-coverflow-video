"""Preview display frame."""

from typing import Callable, Optional, Tuple
import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np
import cv2

from ..widgets.range_slider import RangeSlider
from ..fonts import get_font


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
            font=get_font(),
        )
        self.preview_label.grid(row=0, column=0, padx=10, pady=10)

        # Controls frame
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        controls_frame.grid_columnconfigure(1, weight=1)

        # Frame label
        ctk.CTkLabel(controls_frame, text="Frame:", font=get_font()).grid(row=0, column=0, padx=(0, 10))

        # Frame slider
        self.frame_slider = ctk.CTkSlider(
            controls_frame,
            from_=0,
            to=100,
            command=self._on_slider_change,
        )
        self.frame_slider.set(0)
        self.frame_slider.grid(row=0, column=1, padx=5, sticky="ew")

        # Frame value label (shows total)
        self.frame_label = ctk.CTkLabel(controls_frame, text="/ 100", width=50, font=get_font())
        self.frame_label.grid(row=0, column=2, padx=(5, 0))

        # Frame number entry
        self.frame_entry = ctk.CTkEntry(controls_frame, width=60, font=get_font())
        self.frame_entry.insert(0, "0")
        self.frame_entry.grid(row=0, column=3, padx=5)
        self.frame_entry.bind("<Return>", self._on_entry_submit)
        self.frame_entry.bind("<FocusOut>", self._on_entry_submit)

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            controls_frame,
            text="Refresh",
            width=80,
            command=self._on_refresh_click,
            font=get_font(),
        )
        self.refresh_btn.grid(row=0, column=4)

        # Range controls frame
        range_frame = ctk.CTkFrame(self, fg_color="transparent")
        range_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        range_frame.grid_columnconfigure(1, weight=1)

        # Range label
        ctk.CTkLabel(range_frame, text="Range:", font=get_font()).grid(row=0, column=0, padx=(0, 10))

        # Range slider
        self.range_slider = RangeSlider(
            range_frame,
            from_=0,
            to=100,
            command=self._on_range_change,
        )
        self.range_slider.grid(row=0, column=1, padx=5, sticky="ew")

        # Range info label
        self.range_label = ctk.CTkLabel(range_frame, text="0 - 100 (101 frames)", width=150, font=get_font())
        self.range_label.grid(row=0, column=2, padx=(5, 0))

        # Reset range button
        self.reset_range_btn = ctk.CTkButton(
            range_frame,
            text="Reset",
            width=60,
            command=self._on_reset_range,
            font=get_font(),
        )
        self.reset_range_btn.grid(row=0, column=3, padx=(5, 0))

    def _on_slider_change(self, value: float):
        """Handle frame slider change."""
        frame = int(value)
        self.frame_label.configure(text=f"/ {self._total_frames}")
        self.frame_entry.delete(0, "end")
        self.frame_entry.insert(0, str(frame))
        if self.on_frame_change:
            self.on_frame_change(frame)

    def _on_entry_submit(self, event=None):
        """Handle frame entry submission."""
        try:
            frame = int(self.frame_entry.get())
            frame = max(0, min(frame, self._total_frames - 1))
            self.frame_slider.set(frame)
            self.frame_entry.delete(0, "end")
            self.frame_entry.insert(0, str(frame))
            if self.on_frame_change:
                self.on_frame_change(frame)
        except ValueError:
            # Invalid input, reset to slider value
            current = int(self.frame_slider.get())
            self.frame_entry.delete(0, "end")
            self.frame_entry.insert(0, str(current))

    def _on_refresh_click(self):
        """Handle refresh button click."""
        if self.on_refresh:
            self.on_refresh()

    def _on_range_change(self, start: int, end: int):
        """Handle range slider change."""
        frames = end - start + 1
        self.range_label.configure(text=f"{start} - {end} ({frames} frames)")

    def _on_reset_range(self):
        """Reset range to full range."""
        self.range_slider.reset()
        start, end = self.range_slider.get()
        frames = end - start + 1
        self.range_label.configure(text=f"{start} - {end} ({frames} frames)")

    def set_total_frames(self, total: int):
        """Set the total number of frames for the slider."""
        new_total = max(1, total)

        # Only update if total changed
        if new_total == self._total_frames:
            return

        self._total_frames = new_total
        self.frame_slider.configure(to=self._total_frames - 1)
        self.frame_label.configure(text=f"/ {self._total_frames}")

        # Update range slider bounds, preserving current selection if valid
        current_start, current_end = self.range_slider.get()
        self.range_slider.configure_range(0, self._total_frames - 1)

        # Clamp current range to new bounds
        new_start = min(current_start, self._total_frames - 1)
        new_end = min(current_end, self._total_frames - 1)
        if new_start > new_end:
            new_start = new_end

        self.range_slider.set_range(new_start, new_end)
        frames = new_end - new_start + 1
        self.range_label.configure(text=f"{new_start} - {new_end} ({frames} frames)")

    def get_frame_number(self) -> int:
        """Get the currently selected frame number.

        Also syncs the entry field value to the slider if it differs.
        """
        # Sync entry value to slider (in case user typed but didn't submit)
        try:
            entry_value = int(self.frame_entry.get())
            entry_value = max(0, min(entry_value, self._total_frames - 1))
            current_slider = int(self.frame_slider.get())
            if entry_value != current_slider:
                self.frame_slider.set(entry_value)
                self.frame_entry.delete(0, "end")
                self.frame_entry.insert(0, str(entry_value))
        except ValueError:
            pass  # Invalid entry, just use slider value
        return int(self.frame_slider.get())

    def set_frame_number(self, frame: int):
        """Set the current frame number."""
        self.frame_slider.set(frame)
        self.frame_entry.delete(0, "end")
        self.frame_entry.insert(0, str(frame))
        self.frame_label.configure(text=f"/ {self._total_frames}")

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
        preview_width = self.winfo_width() - 20
        preview_height = self.winfo_height() - 120

        # Use minimum sensible size if widget not yet rendered
        if preview_width < 100:
            preview_width = 400
        if preview_height < 100:
            preview_height = 300

        # Calculate scale to fit (only scale down, never up)
        scale = min(
            preview_width / pil_image.width,
            preview_height / pil_image.height,
            1.0,
        )
        new_width = int(pil_image.width * scale)
        new_height = int(pil_image.height * scale)

        pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

        # Convert to PhotoImage (bypass CTkImage DPI scaling issues)
        photo_image = ImageTk.PhotoImage(pil_image)

        self.preview_label.configure(image=photo_image, text="", width=new_width, height=new_height)
        self._current_image = photo_image  # Keep reference to prevent garbage collection

    def set_loading(self, loading: bool = True):
        """Show loading state."""
        if loading:
            # Clear image first to avoid pyimage reference errors
            self._current_image = None
            self.preview_label.configure(image="", text="Loading preview...")
            self.refresh_btn.configure(state="disabled")
        else:
            self.refresh_btn.configure(state="normal")

    def show_error(self, message: str):
        """Show an error message in the preview area."""
        self._current_image = None
        self.preview_label.configure(image="", text=message)

    def get_render_range(self) -> Tuple[Optional[int], Optional[int]]:
        """Get the selected render range.

        Returns:
            Tuple of (start_frame, end_frame), or (None, None) if full range is selected.
        """
        start, end = self.range_slider.get()
        # If full range, return None to indicate no range restriction
        if start == 0 and end == self._total_frames - 1:
            return (None, None)
        return (start, end)

    def set_render_range(self, start: Optional[int], end: Optional[int]):
        """Set the render range.

        Args:
            start: Start frame, or None for beginning.
            end: End frame, or None for end.
        """
        if start is None:
            start = 0
        if end is None:
            end = self._total_frames - 1

        # Clamp to valid bounds
        start = max(0, min(start, self._total_frames - 1))
        end = max(0, min(end, self._total_frames - 1))
        if start > end:
            start = end

        self.range_slider.set_range(start, end)
        frames = end - start + 1
        self.range_label.configure(text=f"{start} - {end} ({frames} frames)")
