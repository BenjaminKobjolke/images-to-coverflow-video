"""Reflection settings frame."""

import customtkinter as ctk
from ..widgets import LabeledSlider
from ..fonts import get_font


class ReflectionFrame(ctk.CTkFrame):
    """Frame for reflection settings (opacity and length)."""

    def __init__(self, master, **kwargs):
        """Initialize the reflection settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Reflection", font=get_font(weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Reflection opacity
        self.reflection_slider = LabeledSlider(
            self,
            label="Opacity",
            from_=0.0,
            to=1.0,
            default=0.2,
            decimal_places=2,
        )
        self.reflection_slider.pack(fill="x", padx=10, pady=2)

        # Reflection length
        self.reflection_length_slider = LabeledSlider(
            self,
            label="Length",
            from_=0.0,
            to=1.0,
            default=0.5,
            decimal_places=2,
        )
        self.reflection_length_slider.pack(fill="x", padx=10, pady=(2, 10))

    def get_values(self) -> dict:
        """Get all reflection values."""
        return {
            "reflection": self.reflection_slider.get(),
            "reflection_length": self.reflection_length_slider.get(),
        }

    def set_values(self, values: dict):
        """Set reflection values."""
        if "reflection" in values:
            self.reflection_slider.set(values["reflection"])
        if "reflection_length" in values:
            self.reflection_length_slider.set(values["reflection_length"])
