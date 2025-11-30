"""Source folder selection frame."""

from typing import Callable, Optional
import os
import customtkinter as ctk
from ..widgets import FolderPicker


class SourceFrame(ctk.CTkFrame):
    """Frame for source folder selection."""

    def __init__(
        self,
        master,
        command: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """Initialize the source frame.

        Args:
            master: Parent widget.
            command: Callback when source folder changes.
        """
        super().__init__(master, **kwargs)

        self.user_command = command

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Source", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Folder picker
        self.folder_picker = FolderPicker(
            self,
            label="Image Folder",
            command=self._on_folder_change,
        )
        self.folder_picker.pack(fill="x", padx=10, pady=5)

        # Image count display
        self.count_label = ctk.CTkLabel(self, text="No folder selected")
        self.count_label.pack(anchor="w", padx=10, pady=(0, 10))

    def _on_folder_change(self, path: str):
        """Handle folder selection change."""
        self._update_count(path)
        if self.user_command:
            self.user_command(path)

    def _update_count(self, path: str):
        """Update the image count display."""
        if not path or not os.path.isdir(path):
            self.count_label.configure(text="No folder selected")
            return

        # Count image files
        extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
        count = sum(
            1
            for f in os.listdir(path)
            if os.path.splitext(f)[1].lower() in extensions
        )
        self.count_label.configure(text=f"{count} images found")

    def get(self) -> str:
        """Get the selected folder path."""
        return self.folder_picker.get()

    def set(self, path: str):
        """Set the folder path."""
        self.folder_picker.set(path)
        self._update_count(path)
