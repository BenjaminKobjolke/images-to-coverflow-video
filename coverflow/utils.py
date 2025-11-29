"""Utility functions for coverflow video generation."""


def ease_in_out_cubic(t: float) -> float:
    """Cubic easing function for smooth animations."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2
