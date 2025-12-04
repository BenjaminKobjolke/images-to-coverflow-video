"""Playback settings frame."""

import customtkinter as ctk
from ..widgets import LabeledSlider
from ..fonts import get_font


class PlaybackFrame(ctk.CTkFrame):
    """Frame for playback settings (motion blur, repeat, loop)."""

    def __init__(self, master, **kwargs):
        """Initialize the playback settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Playback", font=get_font(weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Motion blur (sub-frames for blending)
        self.motion_blur_slider = LabeledSlider(
            self,
            label="Motion Blur",
            from_=0,
            to=8,
            default=0,
            decimal_places=0,
        )
        self.motion_blur_slider.pack(fill="x", padx=10, pady=2)

        # Repeat checkbox
        self.repeat_var = ctk.BooleanVar(value=False)
        self.repeat_check = ctk.CTkCheckBox(
            self,
            text="Repeat (loop images for seamless sides)",
            variable=self.repeat_var,
        )
        self.repeat_check.pack(anchor="w", padx=10, pady=(5, 2))

        # Loop checkbox
        self.loop_var = ctk.BooleanVar(value=False)
        self.loop_check = ctk.CTkCheckBox(
            self,
            text="Loop (transition back to first image)",
            variable=self.loop_var,
        )
        self.loop_check.pack(anchor="w", padx=10, pady=(2, 10))

    def get_values(self) -> dict:
        """Get all playback values."""
        return {
            "motion_blur": int(self.motion_blur_slider.get()),
            "repeat": self.repeat_var.get(),
            "loop": self.loop_var.get(),
        }

    def set_values(self, values: dict):
        """Set playback values."""
        if "motion_blur" in values:
            self.motion_blur_slider.set(values["motion_blur"])
        if "repeat" in values:
            self.repeat_var.set(values["repeat"])
        if "loop" in values:
            self.loop_var.set(values["loop"])
