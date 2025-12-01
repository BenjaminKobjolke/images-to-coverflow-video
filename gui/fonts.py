"""Font utilities for the GUI application."""
import customtkinter as ctk

from .settings import load_settings


def get_font(size_offset: int = 0, weight: str = "normal") -> ctk.CTkFont:
    """Get a font with the user's configured base size.

    Args:
        size_offset: Offset from the base font size (can be negative)
        weight: Font weight ("normal" or "bold")

    Returns:
        CTkFont with the calculated size
    """
    settings = load_settings()
    base_size = settings.get("font_size", 14)
    return ctk.CTkFont(size=base_size + size_offset, weight=weight)
