"""Reusable slider widget with label and editable value input."""

from typing import Callable, Optional
import customtkinter as ctk

from ..fonts import get_font


class LabeledSlider(ctk.CTkFrame):
    """A slider with a label and editable value input."""

    def __init__(
        self,
        master,
        label: str,
        from_: float,
        to: float,
        default: float,
        step: Optional[float] = None,
        decimal_places: int = 2,
        command: Optional[Callable[[float], None]] = None,
        **kwargs
    ):
        """Initialize the labeled slider.

        Args:
            master: Parent widget.
            label: Label text to display.
            from_: Minimum value.
            to: Maximum value.
            default: Default/initial value.
            step: Step increment (None for continuous).
            decimal_places: Number of decimal places to display.
            command: Callback function when value changes.
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        self.from_ = from_
        self.to = to
        self.decimal_places = decimal_places
        self.step = step
        self.user_command = command
        self._value = default
        self._updating = False  # Prevent recursive updates

        # Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # Label
        self.label = ctk.CTkLabel(self, text=label, width=120, anchor="w", font=get_font())
        self.label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Slider
        self.slider = ctk.CTkSlider(
            self,
            from_=from_,
            to=to,
            command=self._on_slider_change,
        )
        self.slider.set(default)
        self.slider.grid(row=0, column=1, padx=5, sticky="ew")

        # Editable value entry
        self.value_var = ctk.StringVar(value=self._format_value(default))
        self.value_entry = ctk.CTkEntry(
            self,
            textvariable=self.value_var,
            width=60,
            justify="center",
            font=get_font(),
        )
        self.value_entry.grid(row=0, column=2, padx=(10, 0), sticky="e")

        # Bind entry events
        self.value_entry.bind("<Return>", self._on_entry_submit)
        self.value_entry.bind("<FocusOut>", self._on_entry_submit)

    def _format_value(self, value: float) -> str:
        """Format the value for display."""
        if self.decimal_places == 0:
            return str(int(value))
        return f"{value:.{self.decimal_places}f}"

    def _on_slider_change(self, value: float):
        """Handle slider value changes."""
        if self._updating:
            return

        # Apply step if specified
        if self.step is not None:
            value = round(value / self.step) * self.step

        self._value = value

        # Update entry without triggering recursion
        self._updating = True
        self.value_var.set(self._format_value(value))
        self._updating = False

        if self.user_command:
            self.user_command(value)

    def _on_entry_submit(self, event=None):
        """Handle entry value submission."""
        if self._updating:
            return

        try:
            value = float(self.value_var.get())

            # Clamp to range
            value = max(self.from_, min(self.to, value))

            # Apply step if specified
            if self.step is not None:
                value = round(value / self.step) * self.step

            self._value = value

            # Update both entry and slider
            self._updating = True
            self.value_var.set(self._format_value(value))
            self.slider.set(value)
            self._updating = False

            if self.user_command:
                self.user_command(value)

        except ValueError:
            # Reset to current value if invalid input
            self._updating = True
            self.value_var.set(self._format_value(self._value))
            self._updating = False

    def get(self) -> float:
        """Get the current slider value."""
        return self._value

    def set(self, value: float):
        """Set the slider value."""
        # Clamp to range
        value = max(self.from_, min(self.to, value))

        self._value = value

        self._updating = True
        self.slider.set(value)
        self.value_var.set(self._format_value(value))
        self._updating = False

    def set_enabled(self, enabled: bool):
        """Enable or disable the slider and entry."""
        state = "normal" if enabled else "disabled"
        self.slider.configure(state=state)
        self.value_entry.configure(state=state)
