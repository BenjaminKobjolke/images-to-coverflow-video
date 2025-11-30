"""Reusable numeric entry widget with label and validation."""

from typing import Callable, Optional, Union
import customtkinter as ctk


class LabeledEntry(ctk.CTkFrame):
    """A numeric entry with a label and validation."""

    def __init__(
        self,
        master,
        label: str,
        default: Union[int, float],
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        is_int: bool = True,
        width: int = 80,
        command: Optional[Callable[[Union[int, float]], None]] = None,
        **kwargs
    ):
        """Initialize the labeled entry.

        Args:
            master: Parent widget.
            label: Label text to display.
            default: Default/initial value.
            min_value: Minimum allowed value.
            max_value: Maximum allowed value.
            is_int: Whether the value should be an integer.
            width: Width of the entry field.
            command: Callback function when value changes.
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        self.min_value = min_value
        self.max_value = max_value
        self.is_int = is_int
        self.user_command = command
        self._value = default

        # Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Label
        self.label = ctk.CTkLabel(self, text=label, width=120, anchor="w")
        self.label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Entry
        self.var = ctk.StringVar(value=str(default))
        self.entry = ctk.CTkEntry(self, textvariable=self.var, width=width)
        self.entry.grid(row=0, column=1, sticky="w")

        # Bind validation
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Return>", self._on_focus_out)

    def _on_focus_out(self, event=None):
        """Validate and apply the value when focus leaves the entry."""
        try:
            value = int(self.var.get()) if self.is_int else float(self.var.get())

            # Clamp to range
            if self.min_value is not None:
                value = max(self.min_value, value)
            if self.max_value is not None:
                value = min(self.max_value, value)

            self._value = value
            self.var.set(str(value))

            if self.user_command:
                self.user_command(value)

        except ValueError:
            # Reset to last valid value
            self.var.set(str(self._value))

    def get(self) -> Union[int, float]:
        """Get the current entry value."""
        self._on_focus_out()  # Ensure validation
        return self._value

    def set(self, value: Union[int, float]):
        """Set the entry value."""
        if self.is_int:
            value = int(value)
        self._value = value
        self.var.set(str(value))
