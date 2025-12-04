"""Perspective settings frame."""

import customtkinter as ctk
from ..widgets import LabeledSlider
from ..fonts import get_font


class PerspectiveFrame(ctk.CTkFrame):
    """Frame for perspective settings."""

    def __init__(self, master, **kwargs):
        """Initialize the perspective settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Perspective", font=get_font(weight="bold")
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
        self.perspective_slider.pack(fill="x", padx=10, pady=(2, 10))

    def get_values(self) -> dict:
        """Get perspective values."""
        return {
            "perspective": self.perspective_slider.get(),
        }

    def set_values(self, values: dict):
        """Set perspective values."""
        if "perspective" in values:
            self.perspective_slider.set(values["perspective"])

    def set_perspective_enabled(self, enabled: bool):
        """Enable or disable the perspective slider."""
        self.perspective_slider.set_enabled(enabled)
