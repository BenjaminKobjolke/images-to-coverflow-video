"""File and folder picker widgets."""

from typing import Callable, Optional, Tuple
from tkinter import filedialog
import customtkinter as ctk

from ..fonts import get_font


class FilePicker(ctk.CTkFrame):
    """A file picker with label, entry, and browse button."""

    def __init__(
        self,
        master,
        label: str,
        filetypes: Optional[Tuple[Tuple[str, str], ...]] = None,
        default: str = "",
        save_mode: bool = False,
        command: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """Initialize the file picker.

        Args:
            master: Parent widget.
            label: Label text to display.
            filetypes: Tuple of (description, pattern) for file types.
            default: Default file path.
            save_mode: If True, use save dialog instead of open dialog.
            command: Callback function when file is selected.
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        self.filetypes = filetypes or (("All files", "*.*"),)
        self.save_mode = save_mode
        self.user_command = command

        # Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # Label
        self.label = ctk.CTkLabel(self, text=label, width=120, anchor="w", font=get_font())
        self.label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Entry
        self.var = ctk.StringVar(value=default)
        self.entry = ctk.CTkEntry(self, textvariable=self.var, font=get_font())
        self.entry.grid(row=0, column=1, padx=5, sticky="ew")

        # Browse button
        self.browse_btn = ctk.CTkButton(
            self, text="Browse", width=70, command=self._browse, font=get_font()
        )
        self.browse_btn.grid(row=0, column=2, sticky="e")

    def _browse(self):
        """Open file dialog to select a file."""
        if self.save_mode:
            path = filedialog.asksaveasfilename(
                filetypes=self.filetypes,
                defaultextension=".mp4",
            )
        else:
            path = filedialog.askopenfilename(filetypes=self.filetypes)

        if path:
            self.var.set(path)
            if self.user_command:
                self.user_command(path)

    def get(self) -> str:
        """Get the current file path."""
        return self.var.get()

    def set(self, path: str):
        """Set the file path."""
        self.var.set(path)


class FolderPicker(ctk.CTkFrame):
    """A folder picker with label, entry, and browse button."""

    def __init__(
        self,
        master,
        label: str,
        default: str = "",
        command: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """Initialize the folder picker.

        Args:
            master: Parent widget.
            label: Label text to display.
            default: Default folder path.
            command: Callback function when folder is selected.
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        self.user_command = command

        # Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # Label
        self.label = ctk.CTkLabel(self, text=label, width=120, anchor="w", font=get_font())
        self.label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Entry
        self.var = ctk.StringVar(value=default)
        self.entry = ctk.CTkEntry(self, textvariable=self.var, font=get_font())
        self.entry.grid(row=0, column=1, padx=5, sticky="ew")

        # Browse button
        self.browse_btn = ctk.CTkButton(
            self, text="Browse", width=70, command=self._browse, font=get_font()
        )
        self.browse_btn.grid(row=0, column=2, sticky="e")

    def _browse(self):
        """Open folder dialog to select a folder."""
        path = filedialog.askdirectory()

        if path:
            self.var.set(path)
            if self.user_command:
                self.user_command(path)

    def get(self) -> str:
        """Get the current folder path."""
        return self.var.get()

    def set(self, path: str):
        """Set the folder path."""
        self.var.set(path)
