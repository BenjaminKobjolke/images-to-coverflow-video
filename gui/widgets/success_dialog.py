"""Success dialog with Open button for video generation."""

import os
import platform
import subprocess
from pathlib import Path
import customtkinter as ctk


def open_file(filepath: str):
    """Open file with default application."""
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", filepath])
    else:  # Linux
        subprocess.Popen(["xdg-open", filepath])


def open_folder(filepath: str):
    """Open folder containing the file and select it."""
    path = Path(filepath).resolve()
    folder = path.parent

    if platform.system() == "Windows":
        # Explorer with file selected
        subprocess.Popen(["explorer", "/select,", str(path)])
    elif platform.system() == "Darwin":
        # Finder with file selected
        subprocess.Popen(["open", "-R", str(path)])
    else:  # Linux
        # Just open the folder
        subprocess.Popen(["xdg-open", str(folder)])


class SuccessDialog(ctk.CTkToplevel):
    """Modal success dialog with Open button."""

    def __init__(self, master, filepath: str, **kwargs):
        """Initialize the success dialog.

        Args:
            master: Parent widget.
            filepath: Path to the generated video file.
        """
        super().__init__(master, **kwargs)

        self.filepath = filepath

        # Window setup
        self.title("Success")
        self.geometry("450x180")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 450) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 180) // 2
        self.geometry(f"+{x}+{y}")

        # Layout
        self.grid_columnconfigure(0, weight=1)

        # Success icon/text
        success_label = ctk.CTkLabel(
            self,
            text="Video Generated Successfully!",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        success_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Filepath label
        filepath_label = ctk.CTkLabel(
            self,
            text=f"Saved to: {filepath}",
            wraplength=410,
        )
        filepath_label.grid(row=1, column=0, padx=20, pady=5)

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=(15, 20))

        # Open button
        open_btn = ctk.CTkButton(
            button_frame,
            text="Open Video",
            width=100,
            command=self._on_open,
        )
        open_btn.pack(side="left", padx=5)

        # Open folder button
        folder_btn = ctk.CTkButton(
            button_frame,
            text="Open Folder",
            width=100,
            command=self._on_open_folder,
        )
        folder_btn.pack(side="left", padx=5)

        # Close button
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            width=80,
            fg_color="gray",
            command=self._on_close,
        )
        close_btn.pack(side="left", padx=5)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_open(self):
        """Open the video file."""
        try:
            open_file(self.filepath)
        except Exception as e:
            print(f"Error opening file: {e}")
        self._on_close()

    def _on_open_folder(self):
        """Open the folder containing the video."""
        try:
            open_folder(self.filepath)
        except Exception as e:
            print(f"Error opening folder: {e}")
        self._on_close()

    def _on_close(self):
        """Close the dialog."""
        self.grab_release()
        self.destroy()
