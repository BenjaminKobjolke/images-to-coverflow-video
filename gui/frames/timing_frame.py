"""Timing settings frame."""

import customtkinter as ctk
from ..widgets import LabeledSlider


class TimingFrame(ctk.CTkFrame):
    """Frame for timing settings (transition and hold duration)."""

    def __init__(self, master, **kwargs):
        """Initialize the timing settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Timing", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Transition duration
        self.transition_slider = LabeledSlider(
            self,
            label="Transition (s)",
            from_=0.1,
            to=10.0,
            default=2.0,
            decimal_places=1,
        )
        self.transition_slider.pack(fill="x", padx=10, pady=2)

        # Hold duration
        self.hold_slider = LabeledSlider(
            self,
            label="Hold (s)",
            from_=0.1,
            to=10.0,
            default=2.0,
            decimal_places=1,
        )
        self.hold_slider.pack(fill="x", padx=10, pady=(2, 10))

    def get_values(self) -> dict:
        """Get all timing values."""
        return {
            "transition": self.transition_slider.get(),
            "hold": self.hold_slider.get(),
        }

    def set_values(self, values: dict):
        """Set timing values."""
        if "transition" in values:
            self.transition_slider.set(values["transition"])
        if "hold" in values:
            self.hold_slider.set(values["hold"])
