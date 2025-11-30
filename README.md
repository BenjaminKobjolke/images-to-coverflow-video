# images-to-coverflow-video

Convert a sequence of images to a video showing a coverflow effect.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage (arc mode - 3D carousel)
python main.py --source input/ --width 800 --height 600 --transition 2 --hold 2

# Flat mode (straight row, no 3D perspective)
python main.py --source input/ --width 1400 --height 800 --mode flat --visible-range 5 --spacing 0.15

# With custom background and reflections
python main.py --source input/ --background bg.png --reflection 0.3 --repeat
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--source` | (required) | Source directory containing images |
| `--width` | 800 | Output video width in pixels |
| `--height` | 600 | Output video height in pixels |
| `--transition` | 2.0 | Transition duration in seconds |
| `--hold` | 2.0 | Hold duration for each image in seconds |
| `--fps` | 30 | Frames per second |
| `--output` | output.mp4 | Output video file path |
| `--background` | (none) | Background image file (optional) |
| `--perspective` | 0.3 | Perspective/rotation amount for side images (0 = no rotation) |
| `--side-scale` | 0.8 | Scale factor per position from center (0.8 = each image is 80% of previous) |
| `--visible-range` | 3 | Number of images visible on each side of center |
| `--spacing` | 0.35 | Horizontal spacing between images (lower = closer together) |
| `--reflection` | 0.2 | Reflection opacity (0 = no reflection, 1 = full opacity) |
| `--reflection-length` | 0.5 | Length of reflection as fraction of image height (0.0-1.0) |
| `--repeat` | false | Loop images so there's always content on both sides |
| `--mode` | arc | Layout mode: `arc` (3D carousel) or `flat` (straight row, no perspective) |
| `--alignment` | center | Vertical alignment: `center`, `top`, or `bottom` |

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- WebP (.webp)

## Project Structure

```
images-to-coverflow-video/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
└── coverflow/
    ├── __init__.py            # Package exports
    ├── config.py              # Configuration dataclass
    ├── image_loader.py        # Image loading
    ├── transforms.py          # Image transformations
    ├── renderer.py            # Coverflow frame rendering
    ├── video_generator.py     # Video generation
    └── utils.py               # Utility functions
```
