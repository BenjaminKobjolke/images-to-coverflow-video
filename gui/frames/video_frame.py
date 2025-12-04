"""Video output settings frame."""

import customtkinter as ctk
from ..widgets import LabeledEntry, LabeledSlider, FilePicker
from ..fonts import get_font


class VideoFrame(ctk.CTkFrame):
    """Frame for video output settings."""

    def __init__(self, master, **kwargs):
        """Initialize the video settings frame."""
        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Video Output", font=get_font(weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Width
        self.width_entry = LabeledEntry(
            self,
            label="Width",
            default=800,
            min_value=100,
            max_value=4000,
            is_int=True,
        )
        self.width_entry.pack(fill="x", padx=10, pady=2)

        # Height
        self.height_entry = LabeledEntry(
            self,
            label="Height",
            default=600,
            min_value=100,
            max_value=4000,
            is_int=True,
        )
        self.height_entry.pack(fill="x", padx=10, pady=2)

        # Dimension warning (initially hidden)
        self.dimension_warning = ctk.CTkLabel(
            self,
            text="Width and height should be divisible by 16",
            text_color="orange",
            font=get_font(size_offset=-3),
        )

        # Hook up validation callbacks
        self.width_entry.set_command(self._validate_dimensions)
        self.height_entry.set_command(self._validate_dimensions)

        # FPS
        self.fps_entry = LabeledEntry(
            self,
            label="FPS",
            default=30,
            min_value=1,
            max_value=120,
            is_int=True,
        )
        self.fps_entry.pack(fill="x", padx=10, pady=2)

        # Output file
        self.output_picker = FilePicker(
            self,
            label="Output File",
            filetypes=(("MP4 Video", "*.mp4"), ("All files", "*.*")),
            default="output.mp4",
            save_mode=True,
        )
        self.output_picker.pack(fill="x", padx=10, pady=(2, 10))

        # Encoding section title
        self.encoding_label = ctk.CTkLabel(
            self, text="Encoding", font=get_font(weight="bold")
        )
        self.encoding_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Encoder dropdown
        encoder_frame = ctk.CTkFrame(self, fg_color="transparent")
        encoder_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(encoder_frame, text="Encoder", width=80, anchor="w", font=get_font()).pack(side="left")
        self.encoder_var = ctk.StringVar(value="h264")
        self.encoder_menu = ctk.CTkOptionMenu(
            encoder_frame,
            variable=self.encoder_var,
            values=["h264", "h265"],
            width=120,
            font=get_font(),
            dropdown_font=get_font(),
        )
        self.encoder_menu.pack(side="left", padx=(5, 0))

        # Preset dropdown
        preset_frame = ctk.CTkFrame(self, fg_color="transparent")
        preset_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(preset_frame, text="Preset", width=80, anchor="w", font=get_font()).pack(side="left")
        self.preset_var = ctk.StringVar(value="medium")
        self.preset_menu = ctk.CTkOptionMenu(
            preset_frame,
            variable=self.preset_var,
            values=["ultrafast", "fast", "medium", "slow", "veryslow"],
            width=120,
            font=get_font(),
            dropdown_font=get_font(),
        )
        self.preset_menu.pack(side="left", padx=(5, 0))

        # CRF slider (0-51, lower = better quality)
        self.crf_slider = LabeledSlider(
            self,
            label="CRF (Quality)",
            from_=0,
            to=51,
            default=23,
            decimal_places=0,
        )
        self.crf_slider.pack(fill="x", padx=10, pady=2)

        # Max Bitrate entry (optional) - uses plain text entry for string values like "5000k"
        bitrate_frame = ctk.CTkFrame(self, fg_color="transparent")
        bitrate_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(bitrate_frame, text="Max Bitrate", width=120, anchor="w", font=get_font()).pack(side="left")
        self.max_bitrate_var = ctk.StringVar(value="")
        self.max_bitrate_entry = ctk.CTkEntry(
            bitrate_frame,
            textvariable=self.max_bitrate_var,
            width=80,
            placeholder_text="e.g. 10M"
        )
        self.max_bitrate_entry.pack(side="left", padx=(10, 0))

    def get_values(self) -> dict:
        """Get all video settings values."""
        max_bitrate = self.max_bitrate_entry.get()
        return {
            "width": self.width_entry.get(),
            "height": self.height_entry.get(),
            "fps": self.fps_entry.get(),
            "output": self.output_picker.get(),
            "encoder": self.encoder_var.get(),
            "preset": self.preset_var.get(),
            "crf": int(self.crf_slider.get()),
            "max_bitrate": max_bitrate if max_bitrate else None,
        }

    def set_values(self, values: dict):
        """Set video settings values."""
        if "width" in values:
            self.width_entry.set(values["width"])
        if "height" in values:
            self.height_entry.set(values["height"])
        if "fps" in values:
            self.fps_entry.set(values["fps"])
        if "output" in values:
            self.output_picker.set(values["output"])
        if "encoder" in values:
            self.encoder_var.set(values["encoder"])
        if "preset" in values:
            self.preset_var.set(values["preset"])
        if "crf" in values:
            self.crf_slider.set(values["crf"])
        if "max_bitrate" in values and values["max_bitrate"]:
            self.max_bitrate_var.set(str(values["max_bitrate"]))
        else:
            self.max_bitrate_var.set("")

    def _validate_dimensions(self, *args):
        """Show/hide warning if dimensions aren't divisible by 16."""
        width = self.width_entry._value
        height = self.height_entry._value
        if width % 16 != 0 or height % 16 != 0:
            self.dimension_warning.pack(after=self.height_entry, fill="x", padx=10, pady=2)
        else:
            self.dimension_warning.pack_forget()
