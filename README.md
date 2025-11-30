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

# Preview a specific frame (frame 500) or time (24.2 seconds)
python main.py --source input/ --preview 500
python main.py --source input/ --preview 24.2

# Get video statistics without generating
python main.py --source input/ --statistics

# Load settings from a project file
python main.py --project projects/myproject.json

# Load project and override specific settings
python main.py --project projects/myproject.json --width 1920 --height 1080

# Override boolean settings from project
python main.py --project projects/myproject.json --loop false

# Render only a portion of the video (frames 100-500)
python main.py --source input/ --start-frame 100 --end-frame 500

# High quality encoding (lower CRF = better quality)
python main.py --source input/ --crf 18 --preset slow

# H.265 encoding (smaller file size)
python main.py --source input/ --encoder h265 --crf 23

# Constrained quality (good quality with max file size)
python main.py --source input/ --crf 20 --max-bitrate 10M
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--project` | (none) | Project JSON file to load as base settings (CLI args override) |
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
| `--repeat` | false | Loop images so there's always content on both sides (accepts true/false) |
| `--mode` | arc | Layout mode: `arc` (3D carousel) or `flat` (straight row, no perspective) |
| `--alignment` | center | Vertical alignment: `center`, `top`, or `bottom` |
| `--image-scale` | 0.6 | Maximum image size as fraction of canvas (0.0-1.0) |
| `--image-y` | 0.5 | Vertical position of images (0.0=top, 0.5=center, 1.0=bottom) |
| `--loop` | false | Add transition from last to first image for seamless looping (accepts true/false) |
| `--statistics` | false | Only output video statistics (frames, duration) without generating (accepts true/false) |
| `--preview` | (none) | Render single frame as preview.jpg (integer=frame number, decimal=seconds) |
| `--start-frame` | (none) | Frame number to start rendering from (0-indexed) |
| `--end-frame` | (none) | Frame number to stop rendering at (inclusive) |
| `--encoder` | h264 | Video encoder: `h264` or `h265` (h265 produces smaller files) |
| `--crf` | 23 | Quality level (0-51, lower = better quality, larger file) |
| `--preset` | medium | Encoding speed: `ultrafast`, `fast`, `medium`, `slow`, `veryslow` |
| `--max-bitrate` | (none) | Maximum bitrate cap (e.g., `10M`, `5000k`) for constrained quality |

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
