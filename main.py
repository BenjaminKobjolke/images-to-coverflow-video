#!/usr/bin/env python3
"""
Coverflow Video Generator
Creates a video with coverflow-style transitions from an image sequence.
"""

import argparse

from coverflow import Config, ImageLoader, VideoGenerator


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a coverflow video from an image sequence"
    )
    parser.add_argument(
        "--source", required=True, help="Source directory containing images"
    )
    parser.add_argument(
        "--width", type=int, default=800, help="Output video width (default: 800)"
    )
    parser.add_argument(
        "--height", type=int, default=600, help="Output video height (default: 600)"
    )
    parser.add_argument(
        "--transition",
        type=float,
        default=2.0,
        help="Transition duration in seconds (default: 2)",
    )
    parser.add_argument(
        "--hold",
        type=float,
        default=2.0,
        help="Hold duration for each image in seconds (default: 2)",
    )
    parser.add_argument(
        "--fps", type=int, default=30, help="Frames per second (default: 30)"
    )
    parser.add_argument(
        "--output", default="output.mp4", help="Output video file (default: output.mp4)"
    )
    parser.add_argument(
        "--background", default=None, help="Background image file (optional)"
    )
    parser.add_argument(
        "--perspective",
        type=float,
        default=0.3,
        help="Perspective/rotation amount for side images (0 = no rotation, default: 0.3)"
    )
    parser.add_argument(
        "--side-scale",
        type=float,
        default=0.8,
        help="Scale factor for each position from center (0.7 = each image is 70%% of previous, 1.0 = same size, default: 0.8)"
    )
    parser.add_argument(
        "--visible-range",
        type=int,
        default=3,
        help="Number of images visible on each side of center (default: 3)"
    )
    parser.add_argument(
        "--spacing",
        type=float,
        default=0.35,
        help="Horizontal spacing between images (lower = closer together, default: 0.35)"
    )
    parser.add_argument(
        "--reflection",
        type=float,
        default=0.2,
        help="Reflection opacity (0 = no reflection, 1 = full opacity, default: 0.2)"
    )
    parser.add_argument(
        "--reflection-length",
        type=float,
        default=0.5,
        help="Length of reflection as fraction of image height (0.0-1.0, default: 0.5)"
    )
    parser.add_argument(
        "--repeat",
        action="store_true",
        help="Loop images so there's always content on both sides"
    )
    parser.add_argument(
        "--mode",
        choices=["arc", "flat"],
        default="arc",
        help="Layout mode: 'arc' (circular) or 'flat' (straight row)"
    )
    parser.add_argument(
        "--alignment",
        choices=["center", "top", "bottom"],
        default="center",
        help="Vertical alignment: 'center', 'top', or 'bottom' (default: center)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("Coverflow Video Generator")
    print(f"  Source: {args.source}")
    print(f"  Resolution: {args.width}x{args.height}")
    print(f"  Transition: {args.transition}s")
    print(f"  Hold: {args.hold}s")
    print(f"  FPS: {args.fps}")
    print(f"  Output: {args.output}")
    if args.background:
        print(f"  Background: {args.background}")
    print(f"  Perspective: {args.perspective}")
    print(f"  Side scale: {args.side_scale}")
    print(f"  Visible range: {args.visible_range}")
    print(f"  Spacing: {args.spacing}")
    print(f"  Reflection: {args.reflection}")
    print(f"  Reflection length: {args.reflection_length}")
    print(f"  Repeat: {args.repeat}")
    print(f"  Mode: {args.mode}")
    print(f"  Alignment: {args.alignment}")
    print()

    # Create configuration
    config = Config(
        source=args.source,
        width=args.width,
        height=args.height,
        transition=args.transition,
        hold=args.hold,
        fps=args.fps,
        output=args.output,
        background=args.background,
        perspective=args.perspective,
        side_scale=args.side_scale,
        visible_range=args.visible_range,
        spacing=args.spacing,
        reflection=args.reflection,
        reflection_length=args.reflection_length,
        repeat=args.repeat,
        mode=args.mode,
        alignment=args.alignment,
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
