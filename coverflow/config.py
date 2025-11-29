"""Configuration dataclass for coverflow video generation."""

from dataclasses import dataclass


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
