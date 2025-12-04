"""Utility functions for coverflow video generation."""

import math
from typing import Callable


def linear(t: float) -> float:
    """Linear easing - no easing, constant speed."""
    return t


def ease_in_quad(t: float) -> float:
    """Quadratic easing in - slow start, accelerating."""
    return t * t


def ease_out_quad(t: float) -> float:
    """Quadratic easing out - fast start, decelerating."""
    return 1 - (1 - t) ** 2


def ease_in_out_quad(t: float) -> float:
    """Quadratic easing in-out - slow start and end."""
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


def ease_in_cubic(t: float) -> float:
    """Cubic easing in - slow start, accelerating."""
    return t ** 3


def ease_out_cubic(t: float) -> float:
    """Cubic easing out - fast start, decelerating."""
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    """Cubic easing in-out - slow start and end."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def ease_in_sine(t: float) -> float:
    """Sine easing in - slow start, accelerating."""
    return 1 - math.cos((t * math.pi) / 2)


def ease_out_sine(t: float) -> float:
    """Sine easing out - fast start, decelerating."""
    return math.sin((t * math.pi) / 2)


def ease_in_out_sine(t: float) -> float:
    """Sine easing in-out - slow start and end."""
    return -(math.cos(math.pi * t) - 1) / 2


# Dictionary mapping easing names to functions
EASING_FUNCTIONS = {
    "linear": linear,
    "ease_in_quad": ease_in_quad,
    "ease_out_quad": ease_out_quad,
    "ease_in_out_quad": ease_in_out_quad,
    "ease_in_cubic": ease_in_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,
    "ease_in_sine": ease_in_sine,
    "ease_out_sine": ease_out_sine,
    "ease_in_out_sine": ease_in_out_sine,
}

# List of available easing function names
EASING_NAMES = list(EASING_FUNCTIONS.keys())


def get_easing_function(name: str) -> Callable[[float], float]:
    """Get easing function by name.

    Args:
        name: Name of the easing function.

    Returns:
        The easing function. Defaults to ease_in_out_cubic if name not found.
    """
    return EASING_FUNCTIONS.get(name, ease_in_out_cubic)
