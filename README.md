# images-to-coverflow-video

Convert a sequence of images to a video showing a coverflow effect.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py --source input/ --width 800 --height 600 --transition 2 --hold 2
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
