"""Depth effects settings frame."""

import customtkinter as ctk
from ..widgets import LabeledSlider
from ..fonts import get_font
from coverflow.utils import SIDE_CURVE_NAMES


class DepthEffectsFrame(ctk.CTkFrame):
    """Frame for depth effects settings (side scale, blur, alpha)."""

    def __init__(self, master, **kwargs):
        """Initialize the depth effects settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Depth Effects", font=get_font(weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Side scale with curve dropdown and start index
        side_scale_frame = ctk.CTkFrame(self, fg_color="transparent")
        side_scale_frame.pack(fill="x", padx=10, pady=2)
        side_scale_frame.grid_columnconfigure(0, weight=1)

        self.side_scale_slider = LabeledSlider(
            side_scale_frame,
            label="Side Scale",
            from_=0.1,
            to=1.0,
            default=0.8,
            decimal_places=2,
        )
        self.side_scale_slider.grid(row=0, column=0, sticky="ew")

        self.side_scale_curve = ctk.CTkComboBox(
            side_scale_frame,
            values=SIDE_CURVE_NAMES,
            state="readonly",
            width=100,
            font=get_font(),
            dropdown_font=get_font(),
        )
        self.side_scale_curve.set("exponential")
        self.side_scale_curve.grid(row=0, column=1, padx=(5, 0))

        self.side_scale_start = ctk.CTkEntry(
            side_scale_frame, width=40, font=get_font()
        )
        self.side_scale_start.insert(0, "1")
        self.side_scale_start.grid(row=0, column=2, padx=(5, 0))

        # Side blur with curve dropdown and start index
        side_blur_frame = ctk.CTkFrame(self, fg_color="transparent")
        side_blur_frame.pack(fill="x", padx=10, pady=2)
        side_blur_frame.grid_columnconfigure(0, weight=1)

        self.side_blur_slider = LabeledSlider(
            side_blur_frame,
            label="Side Blur",
            from_=0.0,
            to=20.0,
            default=0.0,
            decimal_places=1,
        )
        self.side_blur_slider.grid(row=0, column=0, sticky="ew")

        self.side_blur_curve = ctk.CTkComboBox(
            side_blur_frame,
            values=SIDE_CURVE_NAMES,
            state="readonly",
            width=100,
            font=get_font(),
            dropdown_font=get_font(),
        )
        self.side_blur_curve.set("linear")
        self.side_blur_curve.grid(row=0, column=1, padx=(5, 0))

        self.side_blur_start = ctk.CTkEntry(
            side_blur_frame, width=40, font=get_font()
        )
        self.side_blur_start.insert(0, "1")
        self.side_blur_start.grid(row=0, column=2, padx=(5, 0))

        # Side alpha with curve dropdown and start index
        side_alpha_frame = ctk.CTkFrame(self, fg_color="transparent")
        side_alpha_frame.pack(fill="x", padx=10, pady=(2, 10))
        side_alpha_frame.grid_columnconfigure(0, weight=1)

        self.side_alpha_slider = LabeledSlider(
            side_alpha_frame,
            label="Side Alpha",
            from_=0.1,
            to=1.0,
            default=1.0,
            decimal_places=2,
        )
        self.side_alpha_slider.grid(row=0, column=0, sticky="ew")

        self.side_alpha_curve = ctk.CTkComboBox(
            side_alpha_frame,
            values=SIDE_CURVE_NAMES,
            state="readonly",
            width=100,
            font=get_font(),
            dropdown_font=get_font(),
        )
        self.side_alpha_curve.set("exponential")
        self.side_alpha_curve.grid(row=0, column=1, padx=(5, 0))

        self.side_alpha_start = ctk.CTkEntry(
            side_alpha_frame, width=40, font=get_font()
        )
        self.side_alpha_start.insert(0, "1")
        self.side_alpha_start.grid(row=0, column=2, padx=(5, 0))

    def get_values(self) -> dict:
        """Get all depth effects values."""
        return {
            "side_scale": self.side_scale_slider.get(),
            "side_blur": self.side_blur_slider.get(),
            "side_alpha": self.side_alpha_slider.get(),
            "side_scale_curve": self.side_scale_curve.get(),
            "side_blur_curve": self.side_blur_curve.get(),
            "side_alpha_curve": self.side_alpha_curve.get(),
            "side_scale_start": int(self.side_scale_start.get() or 1),
            "side_blur_start": int(self.side_blur_start.get() or 1),
            "side_alpha_start": int(self.side_alpha_start.get() or 1),
        }

    def set_values(self, values: dict):
        """Set depth effects values."""
        if "side_scale" in values:
            self.side_scale_slider.set(values["side_scale"])
        if "side_blur" in values:
            self.side_blur_slider.set(values["side_blur"])
        if "side_alpha" in values:
            self.side_alpha_slider.set(values["side_alpha"])
        if "side_scale_curve" in values:
            self.side_scale_curve.set(values["side_scale_curve"])
        if "side_blur_curve" in values:
            self.side_blur_curve.set(values["side_blur_curve"])
        if "side_alpha_curve" in values:
            self.side_alpha_curve.set(values["side_alpha_curve"])
        if "side_scale_start" in values:
            self.side_scale_start.delete(0, "end")
            self.side_scale_start.insert(0, str(values["side_scale_start"]))
        if "side_blur_start" in values:
            self.side_blur_start.delete(0, "end")
            self.side_blur_start.insert(0, str(values["side_blur_start"]))
        if "side_alpha_start" in values:
            self.side_alpha_start.delete(0, "end")
            self.side_alpha_start.insert(0, str(values["side_alpha_start"]))
