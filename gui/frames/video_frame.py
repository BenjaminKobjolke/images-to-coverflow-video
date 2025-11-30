"""Video output settings frame."""

import customtkinter as ctk
from ..widgets import LabeledEntry, FilePicker


class VideoFrame(ctk.CTkFrame):
    """Frame for video output settings."""

    def __init__(self, master, **kwargs):
        """Initialize the video settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Video Output", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Width
        self.width_entry = LabeledEntry(
            self,
            label="Width",
            default=800,
            min_value=100,
            max_value=4000,
            is_int=True,
        )
        self.width_entry.pack(fill="x", padx=10, pady=2)

        # Height
        self.height_entry = LabeledEntry(
            self,
            label="Height",
            default=600,
            min_value=100,
            max_value=4000,
            is_int=True,
        )
        self.height_entry.pack(fill="x", padx=10, pady=2)

        # FPS
        self.fps_entry = LabeledEntry(
            self,
            label="FPS",
            default=30,
            min_value=1,
            max_value=120,
            is_int=True,
        )
        self.fps_entry.pack(fill="x", padx=10, pady=2)

        # Output file
        self.output_picker = FilePicker(
            self,
            label="Output File",
            filetypes=(("MP4 Video", "*.mp4"), ("All files", "*.*")),
            default="output.mp4",
            save_mode=True,
        )
        self.output_picker.pack(fill="x", padx=10, pady=(2, 10))

    def get_values(self) -> dict:
        """Get all video settings values."""
        return {
            "width": self.width_entry.get(),
            "height": self.height_entry.get(),
            "fps": self.fps_entry.get(),
            "output": self.output_picker.get(),
        }

    def set_values(self, values: dict):
        """Set video settings values."""
        if "width" in values:
            self.width_entry.set(values["width"])
        if "height" in values:
            self.height_entry.set(values["height"])
        if "fps" in values:
            self.fps_entry.set(values["fps"])
        if "output" in values:
            self.output_picker.set(values["output"])
