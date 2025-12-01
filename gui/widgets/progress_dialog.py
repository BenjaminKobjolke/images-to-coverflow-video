"""Progress dialog for video generation."""

from typing import Callable, Optional
import customtkinter as ctk

from ..fonts import get_font


class ProgressDialog(ctk.CTkToplevel):
    """Modal progress dialog for long-running operations."""

    def __init__(
        self,
        master,
        title: str = "Processing",
        on_cancel: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """Initialize the progress dialog.

        Args:
            master: Parent widget.
            title: Dialog title.
            on_cancel: Callback function when cancel is pressed.
        """
        super().__init__(master, **kwargs)

        self.on_cancel = on_cancel
        self._cancelled = False

        # Window setup
        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 400) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 180) // 2
        self.geometry(f"+{x}+{y}")

        # Prevent closing via X button
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)

        # Layout
        self.grid_columnconfigure(0, weight=1)

        # Status label
        self.status_label = ctk.CTkLabel(self, text="Initializing...", font=get_font())
        self.status_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, width=360)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=10)
        self.progress_bar.set(0)

        # Frame/percentage label
        self.detail_label = ctk.CTkLabel(self, text="0%", font=get_font())
        self.detail_label.grid(row=2, column=0, padx=20, pady=5)

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            self, text="Cancel", width=100, command=self._on_cancel_click, font=get_font()
        )
        self.cancel_btn.grid(row=3, column=0, pady=(10, 20))

    def _on_close_attempt(self):
        """Handle close button click."""
        self._on_cancel_click()

    def _on_cancel_click(self):
        """Handle cancel button click."""
        self._cancelled = True
        self.cancel_btn.configure(state="disabled", text="Cancelling...")
        if self.on_cancel:
            self.on_cancel()

    def set_progress(self, value: float, current: int = 0, total: int = 0):
        """Update the progress bar.

        Args:
            value: Progress value between 0 and 1.
            current: Current frame number.
            total: Total frame count.
        """
        self.progress_bar.set(value)
        percent = int(value * 100)

        if total > 0:
            self.detail_label.configure(text=f"Frame {current} / {total} ({percent}%)")
        else:
            self.detail_label.configure(text=f"{percent}%")

    def set_status(self, text: str):
        """Update the status text."""
        self.status_label.configure(text=text)

    def is_cancelled(self) -> bool:
        """Check if cancel was requested."""
        return self._cancelled

    def close(self):
        """Close the dialog."""
        self.grab_release()
        self.destroy()
