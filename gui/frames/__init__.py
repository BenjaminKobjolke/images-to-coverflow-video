"""GUI frames for settings panels."""

from .source_frame import SourceFrame
from .video_frame import VideoFrame
from .timing_frame import TimingFrame
from .layout_frame import LayoutFrame
from .perspective_frame import PerspectiveFrame
from .depth_effects_frame import DepthEffectsFrame
from .image_frame import ImageFrame
from .background_frame import BackgroundFrame
from .reflection_frame import ReflectionFrame
from .playback_frame import PlaybackFrame
from .preview_frame import PreviewFrame

__all__ = [
    "SourceFrame",
    "VideoFrame",
    "TimingFrame",
    "LayoutFrame",
    "PerspectiveFrame",
    "DepthEffectsFrame",
    "ImageFrame",
    "BackgroundFrame",
    "ReflectionFrame",
    "PlaybackFrame",
    "PreviewFrame",
]
