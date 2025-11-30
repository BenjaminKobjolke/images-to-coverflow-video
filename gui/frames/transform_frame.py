"""3D transform settings frame."""

import customtkinter as ctk
from ..widgets import LabeledSlider


class TransformFrame(ctk.CTkFrame):
    """Frame for 3D transform settings (perspective and side scale)."""

    def __init__(self, master, **kwargs):
        """Initialize the transform settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="3D Effect", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Perspective
        self.perspective_slider = LabeledSlider(
            self,
            label="Perspective",
            from_=0.0,
            to=1.0,
            default=0.3,
            decimal_places=2,
        )
        self.perspective_slider.pack(fill="x", padx=10, pady=2)

        # Side scale
        self.side_scale_slider = LabeledSlider(
            self,
            label="Side Scale",
            from_=0.1,
            to=1.0,
            default=0.8,
            decimal_places=2,
        )
        self.side_scale_slider.pack(fill="x", padx=10, pady=(2, 10))

    def get_values(self) -> dict:
        """Get all transform values."""
        return {
            "perspective": self.perspective_slider.get(),
            "side_scale": self.side_scale_slider.get(),
        }

    def set_values(self, values: dict):
        """Set transform values."""
        if "perspective" in values:
            self.perspective_slider.set(values["perspective"])
        if "side_scale" in values:
            self.side_scale_slider.set(values["side_scale"])

    def set_perspective_enabled(self, enabled: bool):
        """Enable or disable the perspective slider."""
        self.perspective_slider.set_enabled(enabled)
