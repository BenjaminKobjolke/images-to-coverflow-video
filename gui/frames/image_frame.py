"""Image sizing settings frame."""

import customtkinter as ctk
from ..widgets import LabeledSlider


class ImageFrame(ctk.CTkFrame):
    """Frame for image sizing settings (scale and Y position)."""

    def __init__(self, master, **kwargs):
        """Initialize the image settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Image", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Image scale
        self.image_scale_slider = LabeledSlider(
            self,
            label="Scale",
            from_=0.1,
            to=1.0,
            default=0.6,
            decimal_places=2,
        )
        self.image_scale_slider.pack(fill="x", padx=10, pady=2)

        # Image Y position
        self.image_y_slider = LabeledSlider(
            self,
            label="Y Position",
            from_=0.0,
            to=1.0,
            default=0.5,
            decimal_places=2,
        )
        self.image_y_slider.pack(fill="x", padx=10, pady=(2, 10))

    def get_values(self) -> dict:
        """Get all image values."""
        return {
            "image_scale": self.image_scale_slider.get(),
            "image_y": self.image_y_slider.get(),
        }

    def set_values(self, values: dict):
        """Set image values."""
        if "image_scale" in values:
            self.image_scale_slider.set(values["image_scale"])
        if "image_y" in values:
            self.image_y_slider.set(values["image_y"])
