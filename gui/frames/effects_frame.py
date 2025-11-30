"""Visual effects settings frame."""

import customtkinter as ctk
from ..widgets import LabeledSlider, FilePicker


class EffectsFrame(ctk.CTkFrame):
    """Frame for visual effects settings (background, reflection, repeat)."""

    def __init__(self, master, **kwargs):
        """Initialize the effects settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Effects", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Background image
        self.background_picker = FilePicker(
            self,
            label="Background",
            filetypes=(
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*"),
            ),
        )
        self.background_picker.pack(fill="x", padx=10, pady=2)

        # Reflection opacity
        self.reflection_slider = LabeledSlider(
            self,
            label="Reflection",
            from_=0.0,
            to=1.0,
            default=0.2,
            decimal_places=2,
        )
        self.reflection_slider.pack(fill="x", padx=10, pady=2)

        # Reflection length
        self.reflection_length_slider = LabeledSlider(
            self,
            label="Refl. Length",
            from_=0.0,
            to=1.0,
            default=0.5,
            decimal_places=2,
        )
        self.reflection_length_slider.pack(fill="x", padx=10, pady=2)

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
        """Get all effects values."""
        bg = self.background_picker.get()
        return {
            "background": bg if bg else None,
            "reflection": self.reflection_slider.get(),
            "reflection_length": self.reflection_length_slider.get(),
            "repeat": self.repeat_var.get(),
            "loop": self.loop_var.get(),
        }

    def set_values(self, values: dict):
        """Set effects values."""
        if "background" in values and values["background"]:
            self.background_picker.set(values["background"])
        if "reflection" in values:
            self.reflection_slider.set(values["reflection"])
        if "reflection_length" in values:
            self.reflection_length_slider.set(values["reflection_length"])
        if "repeat" in values:
            self.repeat_var.set(values["repeat"])
        if "loop" in values:
            self.loop_var.set(values["loop"])
