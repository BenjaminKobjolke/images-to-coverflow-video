"""Dual-handle range slider widget for selecting start/end values."""

from typing import Callable, Optional, Tuple
import customtkinter as ctk


class RangeSlider(ctk.CTkFrame):
    """A dual-handle range slider for selecting a range of values."""

    def __init__(
        self,
        master,
        from_: int = 0,
        to: int = 100,
        command: Optional[Callable[[int, int], None]] = None,
        **kwargs
    ):
        """Initialize the range slider.

        Args:
            master: Parent widget.
            from_: Minimum value.
            to: Maximum value.
            command: Callback function when range changes (start, end).
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        self.from_ = from_
        self.to = to
        self.user_command = command
        self._start = from_
        self._end = to
        self._dragging = None  # "start", "end", or None
        self._updating = False

        # Slider dimensions
        self._track_height = 6
        self._handle_radius = 8
        self._padding = 10

        # Colors (will be updated based on theme)
        self._track_color = "#3B3B3B"
        self._range_color = "#1F6AA5"
        self._handle_color = "#1F6AA5"
        self._handle_border = "#FFFFFF"

        # Create canvas for custom drawing
        self.canvas = ctk.CTkCanvas(
            self,
            height=self._handle_radius * 2 + 4,
            highlightthickness=0,
            bg=self._get_bg_color(),
        )
        self.canvas.pack(fill="x", expand=True, padx=5)

        # Bind events
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Initial draw
        self.after(10, self._draw)

    def _get_bg_color(self) -> str:
        """Get background color based on appearance mode."""
        if ctk.get_appearance_mode() == "Dark":
            return "#2B2B2B"
        return "#DBDBDB"

    def _value_to_x(self, value: int) -> float:
        """Convert a value to canvas x coordinate."""
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 200  # Default width before layout
        usable_width = canvas_width - 2 * self._padding - 2 * self._handle_radius
        if self.to == self.from_:
            return self._padding + self._handle_radius
        ratio = (value - self.from_) / (self.to - self.from_)
        return self._padding + self._handle_radius + ratio * usable_width

    def _x_to_value(self, x: float) -> int:
        """Convert canvas x coordinate to a value."""
        canvas_width = self.canvas.winfo_width()
        usable_width = canvas_width - 2 * self._padding - 2 * self._handle_radius
        if usable_width <= 0:
            return self.from_
        ratio = (x - self._padding - self._handle_radius) / usable_width
        ratio = max(0, min(1, ratio))
        value = self.from_ + ratio * (self.to - self.from_)
        return int(round(value))

    def _draw(self, **kwargs):
        """Draw the range slider."""
        # Check if canvas exists (parent calls _draw during __init__)
        if not hasattr(self, 'canvas'):
            return

        self.canvas.delete("all")

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1:
            return

        center_y = canvas_height // 2

        # Draw track (full range)
        track_left = self._padding + self._handle_radius
        track_right = canvas_width - self._padding - self._handle_radius
        self.canvas.create_rectangle(
            track_left,
            center_y - self._track_height // 2,
            track_right,
            center_y + self._track_height // 2,
            fill=self._track_color,
            outline="",
        )

        # Draw selected range
        start_x = self._value_to_x(self._start)
        end_x = self._value_to_x(self._end)
        self.canvas.create_rectangle(
            start_x,
            center_y - self._track_height // 2,
            end_x,
            center_y + self._track_height // 2,
            fill=self._range_color,
            outline="",
        )

        # Draw start handle
        self.canvas.create_oval(
            start_x - self._handle_radius,
            center_y - self._handle_radius,
            start_x + self._handle_radius,
            center_y + self._handle_radius,
            fill=self._handle_color,
            outline=self._handle_border,
            width=2,
            tags="start_handle",
        )

        # Draw end handle
        self.canvas.create_oval(
            end_x - self._handle_radius,
            center_y - self._handle_radius,
            end_x + self._handle_radius,
            center_y + self._handle_radius,
            fill=self._handle_color,
            outline=self._handle_border,
            width=2,
            tags="end_handle",
        )

    def _on_resize(self, event):
        """Handle canvas resize."""
        self.canvas.configure(bg=self._get_bg_color())
        self._draw()

    def _on_click(self, event):
        """Handle mouse click."""
        start_x = self._value_to_x(self._start)
        end_x = self._value_to_x(self._end)

        # Check if clicking on start handle
        if abs(event.x - start_x) <= self._handle_radius + 2:
            self._dragging = "start"
        # Check if clicking on end handle
        elif abs(event.x - end_x) <= self._handle_radius + 2:
            self._dragging = "end"
        # Click on track - move nearest handle
        else:
            if abs(event.x - start_x) < abs(event.x - end_x):
                self._dragging = "start"
            else:
                self._dragging = "end"
            self._on_drag(event)

    def _on_drag(self, event):
        """Handle mouse drag."""
        if not self._dragging:
            return

        value = self._x_to_value(event.x)

        if self._dragging == "start":
            # Don't let start go past end
            value = min(value, self._end)
            value = max(value, self.from_)
            if value != self._start:
                self._start = value
                self._draw()
                if self.user_command:
                    self.user_command(self._start, self._end)
        else:  # end
            # Don't let end go before start
            value = max(value, self._start)
            value = min(value, self.to)
            if value != self._end:
                self._end = value
                self._draw()
                if self.user_command:
                    self.user_command(self._start, self._end)

    def _on_release(self, event):
        """Handle mouse release."""
        self._dragging = None

    def get(self) -> Tuple[int, int]:
        """Get the current range (start, end)."""
        return (self._start, self._end)

    def set_range(self, start: int, end: int):
        """Set both handles."""
        # Clamp and validate
        start = max(self.from_, min(start, self.to))
        end = max(self.from_, min(end, self.to))
        if start > end:
            start, end = end, start

        self._start = start
        self._end = end
        self._draw()

    def configure_range(self, from_: int, to: int):
        """Update the slider's min/max range."""
        self.from_ = from_
        self.to = to

        # Clamp current values to new range
        self._start = max(from_, min(self._start, to))
        self._end = max(from_, min(self._end, to))

        # Ensure start <= end
        if self._start > self._end:
            self._start = self._end

        self._draw()

    def reset(self):
        """Reset to full range."""
        self._start = self.from_
        self._end = self.to
        self._draw()
        if self.user_command:
            self.user_command(self._start, self._end)
