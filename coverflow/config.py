"""Configuration dataclass for coverflow video generation."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for coverflow video generation."""

    source: str
    width: int
    height: int
    transition: float
    hold: float
    fps: int
    output: str
    background: Optional[str] = None
    perspective: float = 0.3
    side_scale: float = 0.8  # Scale factor per position (0.8 = each image is 80% of previous)
    visible_range: int = 3  # Number of images visible on each side
    spacing: float = 0.35  # Horizontal spacing between images (lower = closer together)
    reflection: float = 0.2  # Reflection opacity (0 = no reflection, 1 = full opacity)
    reflection_length: float = 0.5  # Fraction of image height to show in reflection (0.0-1.0)
    repeat: bool = False  # Loop images so there's always content on both sides
    mode: str = "arc"  # "arc" or "flat"
    alignment: str = "center"  # "center", "top", or "bottom"
    image_scale: float = 0.6  # Maximum image size as fraction of canvas (0.0-1.0)
    image_y: float = 0.5  # Vertical position as fraction of canvas height (0=top, 0.5=center, 1=bottom)
    statistics: bool = False  # Only output statistics, don't generate video
    preview: Optional[float] = None  # Preview frame (int=frame number, float=seconds)
