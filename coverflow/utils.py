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


# Side effect curve functions
# Two types: DECAY (for scale/alpha - starts at 1.0) and INCREASE (for blur - starts at 0)

# --- DECAY CURVES (for scale/alpha) ---
# These return 1.0 at center (angle=0) and decrease toward 'value' as angle increases

def decay_linear(value: float, angle: float) -> float:
    """Linear decay - constant rate from 1.0 toward value.

    At angle=0: 1.0, at angle=1: value, at angle=2: 2*value-1
    """
    return 1.0 - (1.0 - value) * angle


def decay_exponential(value: float, angle: float) -> float:
    """Exponential decay - accelerating decrease (default for scale/alpha).

    At angle=0: 1.0, at angle=1: value, at angle=2: value²
    """
    return value ** angle if value > 0 else 1.0


def decay_logarithmic(value: float, angle: float) -> float:
    """Logarithmic decay - fast initial drop, then slowing."""
    if angle <= 0:
        return 1.0
    log_factor = math.log(1 + angle) / math.log(2)
    return value ** log_factor if value > 0 else 1.0


def decay_quadratic(value: float, angle: float) -> float:
    """Quadratic decay - slow start, faster drop at edges."""
    return value ** (angle * angle) if value > 0 else 1.0


def decay_sqrt(value: float, angle: float) -> float:
    """Square root decay - fast initial drop, slower at edges."""
    return value ** math.sqrt(angle) if value > 0 and angle >= 0 else 1.0


# --- INCREASE CURVES (for blur) ---
# These return 0 at center (angle=0) and increase as angle increases

def increase_linear(value: float, angle: float) -> float:
    """Linear increase - constant rate from 0.

    At angle=0: 0, at angle=1: value, at angle=2: 2*value
    """
    return value * angle


def increase_exponential(value: float, angle: float) -> float:
    """Exponential increase - slow start, accelerating.

    At angle=0: 0, increases exponentially
    """
    if angle <= 0:
        return 0.0
    # Use 2^angle - 1 normalized so at angle=1 we get 'value'
    return value * (2 ** angle - 1)


def increase_logarithmic(value: float, angle: float) -> float:
    """Logarithmic increase - fast initial rise, then slowing."""
    if angle <= 0:
        return 0.0
    return value * math.log(1 + angle) / math.log(2)


def increase_quadratic(value: float, angle: float) -> float:
    """Quadratic increase - slow start, faster rise at edges."""
    return value * angle * angle


def increase_sqrt(value: float, angle: float) -> float:
    """Square root increase - fast initial rise, slower at edges."""
    return value * math.sqrt(angle) if angle >= 0 else 0.0


# Dictionaries mapping curve names to functions
DECAY_CURVE_FUNCTIONS = {
    "linear": decay_linear,
    "exponential": decay_exponential,
    "logarithmic": decay_logarithmic,
    "quadratic": decay_quadratic,
    "sqrt": decay_sqrt,
}

INCREASE_CURVE_FUNCTIONS = {
    "linear": increase_linear,
    "exponential": increase_exponential,
    "logarithmic": increase_logarithmic,
    "quadratic": increase_quadratic,
    "sqrt": increase_sqrt,
}

# List of available curve function names (sorted least to most aggressive)
SIDE_CURVE_NAMES = ["quadratic", "exponential", "logarithmic", "sqrt", "linear"]


def apply_decay_curve(value: float, angle: float, curve_name: str) -> float:
    """Apply a decay curve (for scale/alpha - starts at 1.0 at center).

    Args:
        value: The target value at angle=1 (e.g., side_scale=0.8).
        angle: The absolute angle/distance from center (0 = center).
        curve_name: Name of the curve function to use.

    Returns:
        The calculated value (1.0 at center, decreasing outward).
    """
    curve_func = DECAY_CURVE_FUNCTIONS.get(curve_name, decay_exponential)
    return curve_func(value, angle)


def apply_increase_curve(value: float, angle: float, curve_name: str) -> float:
    """Apply an increase curve (for blur - starts at 0 at center).

    Args:
        value: The target value at angle=1 (e.g., side_blur=5.0).
        angle: The absolute angle/distance from center (0 = center).
        curve_name: Name of the curve function to use.

    Returns:
        The calculated value (0 at center, increasing outward).
    """
    curve_func = INCREASE_CURVE_FUNCTIONS.get(curve_name, increase_linear)
    return curve_func(value, angle)
