"""Interface settings dialog."""
import customtkinter as ctk
from tkinter import messagebox

from gui.settings import load_settings, save_settings
from gui.fonts import get_font


class InterfaceSettingsDialog(ctk.CTkToplevel):
    """Dialog for interface settings."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Interface Settings")
        self.geometry("300x280")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 280) // 2
        self.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._load_current_settings()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Main frame with padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Theme row
        theme_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=(0, 20))

        theme_label = ctk.CTkLabel(theme_frame, text="Dark Mode:", font=get_font())
        theme_label.pack(side="left")

        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="",
            onvalue=1,
            offvalue=0,
        )
        self.theme_switch.pack(side="right")

        # Sidebar columns row
        columns_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        columns_frame.pack(fill="x", pady=(0, 20))

        columns_label = ctk.CTkLabel(columns_frame, text="Sidebar Columns:", font=get_font())
        columns_label.pack(side="left")

        self.columns_segmented = ctk.CTkSegmentedButton(
            columns_frame,
            values=["1", "2"],
            width=100,
        )
        self.columns_segmented.pack(side="right")

        # Font size row
        font_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        font_frame.pack(fill="x", pady=(0, 10))

        font_label = ctk.CTkLabel(font_frame, text="Font Size:", font=get_font())
        font_label.pack(side="left")

        # Entry for direct input
        self.font_entry = ctk.CTkEntry(font_frame, width=50, font=get_font())
        self.font_entry.pack(side="right")
        self.font_entry.bind("<Return>", self._on_font_entry_change)
        self.font_entry.bind("<FocusOut>", self._on_font_entry_change)

        # Slider
        self.font_slider = ctk.CTkSlider(
            font_frame,
            from_=14,
            to=24,
            number_of_steps=10,
            width=120,
            command=self._on_font_slider_change,
        )
        self.font_slider.pack(side="right", padx=(0, 10))

        # Restart note
        note_label = ctk.CTkLabel(
            main_frame,
            text="* Restart required for font changes",
            text_color="gray",
            font=get_font(),
        )
        note_label.pack(fill="x", pady=(0, 10))

        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self._on_close,
            width=100,
            font=get_font(),
        )
        close_btn.pack()

    def _load_current_settings(self):
        """Load and apply current settings to widgets."""
        settings = load_settings()

        # Theme
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()

        # Sidebar columns - store original value for restart check
        self._original_columns = settings.get("sidebar_columns", 1)
        self.columns_segmented.set(str(self._original_columns))

        # Font size - store original value for restart check
        self._original_font_size = settings.get("font_size", 14)
        self.font_slider.set(self._original_font_size)
        self.font_entry.delete(0, "end")
        self.font_entry.insert(0, str(self._original_font_size))

    def _on_font_slider_change(self, value):
        """Handle font slider change - update entry field."""
        int_value = int(round(value))
        self.font_entry.delete(0, "end")
        self.font_entry.insert(0, str(int_value))

    def _on_font_entry_change(self, event=None):
        """Handle font entry change - update slider."""
        try:
            value = int(self.font_entry.get())
            # Clamp to valid range
            value = max(14, min(24, value))
            self.font_slider.set(value)
            # Update entry if clamped
            self.font_entry.delete(0, "end")
            self.font_entry.insert(0, str(value))
        except ValueError:
            # Reset to slider value if invalid
            self.font_entry.delete(0, "end")
            self.font_entry.insert(0, str(int(self.font_slider.get())))

    def _on_close(self):
        """Handle close button - apply theme and save settings."""
        is_dark = self.theme_switch.get() == 1
        new_mode = "Dark" if is_dark else "Light"
        new_columns = int(self.columns_segmented.get())
        new_font_size = int(round(self.font_slider.get()))

        # Apply theme
        ctk.set_appearance_mode(new_mode)

        # Save settings
        settings = load_settings()
        settings["theme"] = new_mode
        settings["sidebar_columns"] = new_columns
        settings["font_size"] = new_font_size
        save_settings(settings)

        # Check if restart is needed
        needs_restart = (
            new_columns != self._original_columns or
            new_font_size != self._original_font_size
        )
        if needs_restart:
            messagebox.showinfo(
                "Restart Required",
                "Please restart the application for the changes to take effect."
            )

        self.destroy()
