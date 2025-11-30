#!/usr/bin/env python3
"""
Coverflow Video Generator
Creates a video with coverflow-style transitions from an image sequence.
"""

import argparse
import sys
from pathlib import Path

from coverflow import Config, ImageLoader, VideoGenerator


# Default values for all optional settings
DEFAULTS = {
    "width": 800,
    "height": 600,
    "fps": 30,
    "output": "output.mp4",
    "transition": 2.0,
    "hold": 2.0,
    "perspective": 0.3,
    "side_scale": 0.8,
    "visible_range": 3,
    "spacing": 0.35,
    "reflection": 0.2,
    "reflection_length": 0.5,
    "mode": "arc",
    "alignment": "center",
    "image_scale": 0.6,
    "image_y": 0.5,
    "repeat": False,
    "loop": False,
    "statistics": False,
    "preview": None,
    "background": None,
    "source": None,
    "start_frame": None,
    "end_frame": None,
    "encoder": "h264",
    "crf": 23,
    "preset": "medium",
    "max_bitrate": None,
}


def parse_bool(value: str) -> bool:
    """Parse boolean string value."""
    if value.lower() in ("true", "1", "yes"):
        return True
    elif value.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(f"Boolean value expected, got '{value}'")


def merge_settings(
    project_settings: dict, args: argparse.Namespace, defaults: dict
) -> dict:
    """Merge project settings with CLI arguments.

    Priority: CLI args (if not None) > project settings > hardcoded defaults
    """
    result = defaults.copy()

    # Apply project settings
    result.update(project_settings)

    # Apply CLI overrides (only if explicitly set, i.e., not None)
    for key, value in vars(args).items():
        if value is not None and key != "project":
            result[key] = value

    return result


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a coverflow video from an image sequence"
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project JSON file to load as base settings (CLI args override)",
    )
    parser.add_argument(
        "--source", default=None, help="Source directory containing images"
    )
    parser.add_argument(
        "--width", type=int, default=None, help="Output video width (default: 800)"
    )
    parser.add_argument(
        "--height", type=int, default=None, help="Output video height (default: 600)"
    )
    parser.add_argument(
        "--transition",
        type=float,
        default=None,
        help="Transition duration in seconds (default: 2)",
    )
    parser.add_argument(
        "--hold",
        type=float,
        default=None,
        help="Hold duration for each image in seconds (default: 2)",
    )
    parser.add_argument(
        "--fps", type=int, default=None, help="Frames per second (default: 30)"
    )
    parser.add_argument(
        "--output", default=None, help="Output video file (default: output.mp4)"
    )
    parser.add_argument(
        "--background", default=None, help="Background image file (optional)"
    )
    parser.add_argument(
        "--perspective",
        type=float,
        default=None,
        help="Perspective/rotation amount for side images (0 = no rotation, default: 0.3)",
    )
    parser.add_argument(
        "--side-scale",
        type=float,
        default=None,
        help="Scale factor for each position from center (0.7 = each image is 70%% of previous, 1.0 = same size, default: 0.8)",
    )
    parser.add_argument(
        "--visible-range",
        type=int,
        default=None,
        help="Number of images visible on each side of center (default: 3)",
    )
    parser.add_argument(
        "--spacing",
        type=float,
        default=None,
        help="Horizontal spacing between images (lower = closer together, default: 0.35)",
    )
    parser.add_argument(
        "--reflection",
        type=float,
        default=None,
        help="Reflection opacity (0 = no reflection, 1 = full opacity, default: 0.2)",
    )
    parser.add_argument(
        "--reflection-length",
        type=float,
        default=None,
        help="Length of reflection as fraction of image height (0.0-1.0, default: 0.5)",
    )
    parser.add_argument(
        "--repeat",
        type=parse_bool,
        default=None,
        nargs="?",
        const=True,
        help="Loop images so there's always content on both sides (true/false)",
    )
    parser.add_argument(
        "--loop",
        type=parse_bool,
        default=None,
        nargs="?",
        const=True,
        help="Add transition from last to first image for seamless video looping (true/false)",
    )
    parser.add_argument(
        "--mode",
        choices=["arc", "flat"],
        default=None,
        help="Layout mode: 'arc' (circular) or 'flat' (straight row)",
    )
    parser.add_argument(
        "--alignment",
        choices=["center", "top", "bottom"],
        default=None,
        help="Vertical alignment: 'center', 'top', or 'bottom' (default: center)",
    )
    parser.add_argument(
        "--image-scale",
        type=float,
        default=None,
        help="Maximum image size as fraction of canvas (0.0-1.0, default: 0.6)",
    )
    parser.add_argument(
        "--image-y",
        type=float,
        default=None,
        help="Vertical position of images (0.0=top, 0.5=center, 1.0=bottom, default: 0.5)",
    )
    parser.add_argument(
        "--statistics",
        type=parse_bool,
        default=None,
        nargs="?",
        const=True,
        help="Only output video statistics (frames, duration) without generating (true/false)",
    )
    parser.add_argument(
        "--preview",
        type=float,
        default=None,
        help="Render single frame as preview.jpg (integer=frame number, decimal=seconds)",
    )
    parser.add_argument(
        "--start-frame",
        type=int,
        default=None,
        help="Frame number to start rendering from (0-indexed)",
    )
    parser.add_argument(
        "--end-frame",
        type=int,
        default=None,
        help="Frame number to stop rendering at (inclusive)",
    )
    parser.add_argument(
        "--encoder",
        type=str,
        choices=["h264", "h265"],
        default=None,
        help="Video encoder (h264 or h265)",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=None,
        help="CRF quality value (0-51, lower=better quality, default: 23)",
    )
    parser.add_argument(
        "--preset",
        type=str,
        choices=["ultrafast", "fast", "medium", "slow", "veryslow"],
        default=None,
        help="Encoding preset (ultrafast, fast, medium, slow, veryslow)",
    )
    parser.add_argument(
        "--max-bitrate",
        type=str,
        default=None,
        help="Maximum bitrate (e.g., 10M, 5000k) for constrained quality",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Load project if specified
    project_settings = {}
    if args.project:
        from gui.projects import load_project

        project_settings = load_project(Path(args.project))
        print(f"Loaded project: {args.project}")

    # Merge settings: CLI overrides > project > defaults
    settings = merge_settings(project_settings, args, DEFAULTS)

    # Validate required fields
    if not settings.get("source"):
        print("Error: --source is required (either via CLI or in project file)")
        sys.exit(1)

    # Handle repeat/loop dependency
    if settings["loop"]:
        settings["repeat"] = True

    # Validate dimensions are divisible by 16 for video encoding
    if settings["width"] % 16 != 0 or settings["height"] % 16 != 0:
        print(f"Error: Width ({settings['width']}) and height ({settings['height']}) must be divisible by 16 for video encoding.")
        suggested_w = (settings["width"] // 16) * 16
        suggested_h = (settings["height"] // 16) * 16
        print(f"Suggested dimensions: {suggested_w}x{suggested_h}")
        sys.exit(1)

    print("Coverflow Video Generator")
    print(f"  Source: {settings['source']}")
    print(f"  Resolution: {settings['width']}x{settings['height']}")
    print(f"  Transition: {settings['transition']}s")
    print(f"  Hold: {settings['hold']}s")
    print(f"  FPS: {settings['fps']}")
    print(f"  Output: {settings['output']}")
    if settings["background"]:
        print(f"  Background: {settings['background']}")
    print(f"  Perspective: {settings['perspective']}")
    print(f"  Side scale: {settings['side_scale']}")
    print(f"  Visible range: {settings['visible_range']}")
    print(f"  Spacing: {settings['spacing']}")
    print(f"  Reflection: {settings['reflection']}")
    print(f"  Reflection length: {settings['reflection_length']}")
    print(f"  Repeat: {settings['repeat']}")
    print(f"  Mode: {settings['mode']}")
    print(f"  Alignment: {settings['alignment']}")
    print(f"  Image scale: {settings['image_scale']}")
    print(f"  Image Y: {settings['image_y']}")
    if settings["start_frame"] is not None or settings["end_frame"] is not None:
        start = settings["start_frame"] if settings["start_frame"] is not None else 0
        end = settings["end_frame"] if settings["end_frame"] is not None else "end"
        print(f"  Frame range: {start} - {end}")
    print(f"  Encoder: {settings['encoder']}")
    print(f"  CRF: {settings['crf']}")
    print(f"  Preset: {settings['preset']}")
    if settings["max_bitrate"]:
        print(f"  Max bitrate: {settings['max_bitrate']}")
    print()

    # Create configuration
    config = Config(
        source=settings["source"],
        width=settings["width"],
        height=settings["height"],
        transition=settings["transition"],
        hold=settings["hold"],
        fps=settings["fps"],
        output=settings["output"],
        background=settings["background"],
        perspective=settings["perspective"],
        side_scale=settings["side_scale"],
        visible_range=settings["visible_range"],
        spacing=settings["spacing"],
        reflection=settings["reflection"],
        reflection_length=settings["reflection_length"],
        repeat=settings["repeat"],
        loop=settings["loop"],
        mode=settings["mode"],
        alignment=settings["alignment"],
        image_scale=settings["image_scale"],
        image_y=settings["image_y"],
        statistics=settings["statistics"],
        preview=settings["preview"],
        start_frame=settings["start_frame"],
        end_frame=settings["end_frame"],
        encoder=settings["encoder"],
        crf=settings["crf"],
        preset=settings["preset"],
        max_bitrate=settings["max_bitrate"],
    )

    # Load images
    loader = ImageLoader(config.source)
    images = loader.load_images()

    # Generate video
    generator = VideoGenerator(config)
    generator.generate(images)

    print("Done!")


if __name__ == "__main__":
    main()
