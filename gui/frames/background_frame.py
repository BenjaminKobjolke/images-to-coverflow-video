"""Background settings frame."""

import customtkinter as ctk
from ..widgets import FilePicker
from ..fonts import get_font


class BackgroundFrame(ctk.CTkFrame):
    """Frame for background settings (image, color, gradient)."""

    def __init__(self, master, **kwargs):
        """Initialize the background settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Background", font=get_font(weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Background image
        self.background_picker = FilePicker(
            self,
            label="Image",
            filetypes=(
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*"),
            ),
        )
        self.background_picker.pack(fill="x", padx=10, pady=2)

        # Background color
        bg_color_frame = ctk.CTkFrame(self, fg_color="transparent")
        bg_color_frame.pack(fill="x", padx=10, pady=2)
        bg_color_frame.grid_columnconfigure(0, weight=0)
        bg_color_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bg_color_frame, text="Color", width=120, anchor="w", font=get_font()
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.bg_color_var = ctk.StringVar(value="")
        self.bg_color_entry = ctk.CTkEntry(
            bg_color_frame,
            textvariable=self.bg_color_var,
            placeholder_text="#RRGGBB",
            width=100,
            font=get_font(),
        )
        self.bg_color_entry.grid(row=0, column=1, sticky="w")

        # Background color bottom (for gradient)
        bg_color_bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bg_color_bottom_frame.pack(fill="x", padx=10, pady=(2, 10))
        bg_color_bottom_frame.grid_columnconfigure(0, weight=0)
        bg_color_bottom_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bg_color_bottom_frame, text="Bottom Color", width=120, anchor="w", font=get_font()
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.bg_color_bottom_var = ctk.StringVar(value="")
        self.bg_color_bottom_entry = ctk.CTkEntry(
            bg_color_bottom_frame,
            textvariable=self.bg_color_bottom_var,
            placeholder_text="#RRGGBB",
            width=100,
            font=get_font(),
        )
        self.bg_color_bottom_entry.grid(row=0, column=1, sticky="w")

    def get_values(self) -> dict:
        """Get all background values."""
        bg = self.background_picker.get()
        bg_color = self.bg_color_var.get().strip()
        bg_color_bottom = self.bg_color_bottom_var.get().strip()
        return {
            "background": bg if bg else None,
            "background_color": bg_color if bg_color else None,
            "background_color_bottom": bg_color_bottom if bg_color_bottom else None,
        }

    def set_values(self, values: dict):
        """Set background values."""
        if "background" in values and values["background"]:
            self.background_picker.set(values["background"])
        if "background_color" in values and values["background_color"]:
            self.bg_color_var.set(values["background_color"])
        if "background_color_bottom" in values and values["background_color_bottom"]:
            self.bg_color_bottom_var.set(values["background_color_bottom"])
