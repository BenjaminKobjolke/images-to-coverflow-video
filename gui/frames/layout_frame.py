"""Layout settings frame."""

from typing import Callable, Optional
import customtkinter as ctk
from ..widgets import LabeledSlider


class LayoutFrame(ctk.CTkFrame):
    """Frame for layout settings (mode, alignment, visible range, spacing)."""

    def __init__(
        self,
        master,
        on_mode_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """Initialize the layout settings frame.

        Args:
            master: Parent widget.
            on_mode_change: Callback when mode changes (receives "arc" or "flat").
        """
        super().__init__(master, **kwargs)
        self.on_mode_change = on_mode_change

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Layout", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Mode selection
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=2)
        mode_frame.grid_columnconfigure(0, weight=0)
        mode_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(mode_frame, text="Mode", width=120, anchor="w").grid(
            row=0, column=0, padx=(0, 10), sticky="w"
        )
        self.mode_var = ctk.StringVar(value="arc")
        self.mode_combo = ctk.CTkComboBox(
            mode_frame,
            values=["arc", "flat"],
            variable=self.mode_var,
            command=self._on_mode_selected,
            state="readonly",
            width=150,
        )
        self.mode_combo.grid(row=0, column=1, sticky="w")

        # Alignment selection
        align_frame = ctk.CTkFrame(self, fg_color="transparent")
        align_frame.pack(fill="x", padx=10, pady=2)
        align_frame.grid_columnconfigure(0, weight=0)
        align_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(align_frame, text="Alignment", width=120, anchor="w").grid(
            row=0, column=0, padx=(0, 10), sticky="w"
        )
        self.alignment_var = ctk.StringVar(value="center")
        self.alignment_combo = ctk.CTkComboBox(
            align_frame,
            values=["center", "top", "bottom"],
            variable=self.alignment_var,
            state="readonly",
            width=150,
        )
        self.alignment_combo.grid(row=0, column=1, sticky="w")

        # Visible range
        self.visible_slider = LabeledSlider(
            self,
            label="Visible Range",
            from_=1,
            to=10,
            default=3,
            step=1,
            decimal_places=0,
        )
        self.visible_slider.pack(fill="x", padx=10, pady=2)

        # Spacing
        self.spacing_slider = LabeledSlider(
            self,
            label="Spacing",
            from_=0.05,
            to=1.0,
            default=0.35,
            decimal_places=2,
        )
        self.spacing_slider.pack(fill="x", padx=10, pady=(2, 10))

    def get_values(self) -> dict:
        """Get all layout values."""
        return {
            "mode": self.mode_var.get(),
            "alignment": self.alignment_var.get(),
            "visible_range": int(self.visible_slider.get()),
            "spacing": self.spacing_slider.get(),
        }

    def set_values(self, values: dict):
        """Set layout values."""
        if "mode" in values:
            self.mode_var.set(values["mode"])
            # Trigger callback when setting mode programmatically
            if self.on_mode_change:
                self.on_mode_change(values["mode"])
        if "alignment" in values:
            self.alignment_var.set(values["alignment"])
        if "visible_range" in values:
            self.visible_slider.set(values["visible_range"])
        if "spacing" in values:
            self.spacing_slider.set(values["spacing"])

    def _on_mode_selected(self, mode: str):
        """Handle mode selection change."""
        if self.on_mode_change:
            self.on_mode_change(mode)
