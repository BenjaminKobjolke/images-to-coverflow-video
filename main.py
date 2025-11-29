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
