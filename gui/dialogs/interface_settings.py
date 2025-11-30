"""Interface settings dialog."""
import customtkinter as ctk
from tkinter import messagebox

from gui.settings import load_settings, save_settings


class InterfaceSettingsDialog(ctk.CTkToplevel):
    """Dialog for interface settings."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Interface Settings")
        self.geometry("300x200")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 200) // 2
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

        theme_label = ctk.CTkLabel(theme_frame, text="Dark Mode:")
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

        columns_label = ctk.CTkLabel(columns_frame, text="Sidebar Columns:")
        columns_label.pack(side="left")

        self.columns_segmented = ctk.CTkSegmentedButton(
            columns_frame,
            values=["1", "2"],
            width=100,
        )
        self.columns_segmented.pack(side="right")

        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self._on_close,
            width=100,
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

    def _on_close(self):
        """Handle close button - apply theme and save settings."""
        is_dark = self.theme_switch.get() == 1
        new_mode = "Dark" if is_dark else "Light"
        new_columns = int(self.columns_segmented.get())

        # Apply theme
        ctk.set_appearance_mode(new_mode)

        # Save settings
        settings = load_settings()
        settings["theme"] = new_mode
        settings["sidebar_columns"] = new_columns
        save_settings(settings)

        # Check if restart is needed
        if new_columns != self._original_columns:
            messagebox.showinfo(
                "Restart Required",
                "Please restart the application for the sidebar layout change to take effect."
            )

        self.destroy()
