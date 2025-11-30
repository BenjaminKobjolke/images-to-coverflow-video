# Coverflow Video Generator - GUI Documentation

## Overview

The GUI is a CustomTkinter-based application that provides a graphical interface for the coverflow video generator CLI tool. It preserves full CLI functionality while adding visual controls, preview capabilities, and project management.

## Running the GUI

```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI
python gui.py

# CLI still works independently
python main.py --source input/ --output video.mp4
```

## Architecture

### Entry Point

- **`gui.py`** - Main entry point that creates the root window, menu bar, and keyboard shortcuts

### Package Structure

```
gui/
├── __init__.py          # Exports CoverflowApp
├── app.py               # Main application frame (CoverflowApp class)
├── projects.py          # Project save/load functionality
├── frames/              # UI panels for different settings
│   ├── __init__.py
│   ├── source_frame.py      # Source folder selection
│   ├── video_frame.py       # Width, height, fps, output
│   ├── timing_frame.py      # Transition, hold durations
│   ├── layout_frame.py      # Mode, alignment, visible-range, spacing
│   ├── transform_frame.py   # Perspective, side-scale (3D effects)
│   ├── image_frame.py       # Image scale, Y position
│   ├── effects_frame.py     # Background, reflection, repeat
│   └── preview_frame.py     # Preview canvas and frame slider
├── widgets/             # Reusable UI components
│   ├── __init__.py
│   ├── labeled_slider.py    # Slider with label and editable value
│   ├── labeled_entry.py     # Numeric entry with validation
│   ├── file_picker.py       # File/folder picker dialogs
│   └── progress_dialog.py   # Modal progress dialog
└── workers/             # Background thread workers
    ├── __init__.py
    ├── preview_worker.py    # Threaded preview rendering
    └── video_worker.py      # Threaded video generation
```

## GUI Layout

```
+------------------------------------------------------------------+
| File                                                              |
+------------------------------------------------------------------+
|  LEFT SIDEBAR          |  RIGHT PANEL                            |
|  (scrollable)          |                                         |
|                        |  +----------------------------------+   |
|  === Source ===        |  |                                  |   |
|  [Image Folder]        |  |        PREVIEW CANVAS            |   |
|  12 images found       |  |                                  |   |
|                        |  +----------------------------------+   |
|  === Video Output ===  |  Frame: [====slider====] [Refresh]      |
|  Width: 800            |                                         |
|  Height: 600           +------------------------------------------+
|  FPS: 30               |                                         |
|  Output: [output.mp4]  |  [Generate Video] [Statistics] [Theme]  |
|                        |                                         |
|  === Timing ===        +------------------------------------------+
|  Transition: 2.0s      |
|  Hold: 2.0s            |
|                        |
|  === Layout ===        |
|  Mode: [arc/flat]      |
|  Alignment: [center]   |
|  Visible Range: 3      |
|  Spacing: 0.35         |
|                        |
|  === 3D Effect ===     |
|  Perspective: 0.30     |  <- Disabled when mode=flat
|  Side Scale: 0.80      |
|                        |
|  === Image ===         |
|  Scale: 0.60           |
|  Y Position: 0.50      |
|                        |
|  === Effects ===       |
|  Background: [...]     |
|  Reflection: 0.20      |
|  Refl. Length: 0.50    |
|  [x] Repeat            |
+------------------------+
```

## Menu Bar

```
File
├── New Project          Ctrl+N    - Reset to defaults, clear current project
├── Open Project...      Ctrl+O    - Open .json project file
├── ─────────────────
├── Save Project         Ctrl+S    - Save to current file (or Save As if new)
└── Save Project As...   Ctrl+Shift+S  - Save to new file
```

## Features

### Project Management
- Projects are saved as JSON files in the `projects/` folder
- Projects store ALL settings including paths (source, output, background)
- Standard OS file dialogs for all operations

### Preview System
- Manual preview rendering (click Refresh button)
- Frame slider to preview any frame in the video
- Preview updates when source folder changes

### Video Generation
- Background thread generation (non-blocking UI)
- Progress dialog with frame count and percentage
- Cancel button to abort generation
- Success/error notifications

### Parameter Controls
- All 17 CLI parameters available as GUI controls
- Sliders have editable text input for precise values
- Values are validated and clamped to valid ranges
- Perspective slider is disabled when mode=flat (has no effect)

## Widget Reference

### LabeledSlider
Slider with label and editable value input.

```python
slider = LabeledSlider(
    parent,
    label="Perspective",
    from_=0.0,
    to=1.0,
    default=0.3,
    decimal_places=2,
    step=None,  # Optional step increment
    command=callback,  # Optional change callback
)
slider.get()  # Get current value
slider.set(0.5)  # Set value
slider.set_enabled(False)  # Disable slider
```

### LabeledEntry
Numeric entry with label and validation.

```python
entry = LabeledEntry(
    parent,
    label="Width",
    default=800,
    min_value=100,
    max_value=4000,
    is_int=True,
    command=callback,
)
entry.get()  # Get current value
entry.set(1920)  # Set value
```

### FilePicker / FolderPicker
File and folder selection with browse button.

```python
picker = FilePicker(
    parent,
    label="Background",
    filetypes=(("Images", "*.jpg *.png"), ("All", "*.*")),
    save_mode=False,  # True for save dialog
    command=callback,
)
picker.get()  # Get path
picker.set("/path/to/file")  # Set path
```

### ProgressDialog
Modal dialog for long-running operations.

```python
dialog = ProgressDialog(
    parent,
    title="Generating Video",
    on_cancel=cancel_callback,
)
dialog.set_progress(0.5, current=50, total=100)
dialog.set_status("Processing...")
dialog.close()
```

## Frame Reference

### SourceFrame
- Folder picker for source images
- Shows image count after selection
- Callback when folder changes

### VideoFrame
- Width, Height, FPS entries
- Output file picker (save dialog)

### TimingFrame
- Transition duration slider (0.1-10.0s)
- Hold duration slider (0.1-10.0s)

### LayoutFrame
- Mode dropdown (arc/flat)
- Alignment dropdown (center/top/bottom)
- Visible range slider (1-10)
- Spacing slider (0.05-1.0)
- **on_mode_change callback** for mode-dependent UI updates

### TransformFrame
- Perspective slider (0.0-1.0) - disabled in flat mode
- Side scale slider (0.1-1.0)
- **set_perspective_enabled(bool)** method

### ImageFrame
- Image scale slider (0.1-1.0)
- Y position slider (0.0-1.0)

### EffectsFrame
- Background image picker
- Reflection opacity slider (0.0-1.0)
- Reflection length slider (0.0-1.0)
- Repeat checkbox

### PreviewFrame
- Preview canvas (CTkLabel with image)
- Frame number slider
- Refresh button
- Shows loading state and errors

## Worker Reference

### PreviewWorker
Renders a single frame in background thread.

```python
worker = PreviewWorker(
    config,
    on_complete=lambda img, err: ...,
    frame_number=0,
)
worker.start()
```

### VideoWorker
Generates full video in background thread.

```python
worker = VideoWorker(
    config,
    on_progress=lambda current, total: ...,
    on_complete=lambda success, error: ...,
)
worker.start()
worker.cancel()  # Request cancellation
worker.is_running()  # Check if still running
```

## Project File Format

```json
{
  "project_name": "My Project",
  "project_version": "1.0",
  "settings": {
    "source": "C:/path/to/images",
    "output": "C:/path/to/output.mp4",
    "background": null,
    "width": 800,
    "height": 600,
    "fps": 30,
    "transition": 2.0,
    "hold": 2.0,
    "mode": "arc",
    "alignment": "center",
    "visible_range": 3,
    "spacing": 0.35,
    "perspective": 0.3,
    "side_scale": 0.8,
    "image_scale": 0.6,
    "image_y": 0.5,
    "reflection": 0.2,
    "reflection_length": 0.5,
    "repeat": false
  }
}
```

## Threading Model

- **Main thread**: GUI updates, user interaction
- **Worker threads**: Preview rendering, video generation
- **Communication**: `self.after(0, callback)` schedules callbacks on main thread
- **Cancellation**: `threading.Event` flag checked during generation loops

## Dependencies

```
customtkinter==5.2.2
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
```

## Extending the GUI

### Adding a New Setting

1. Add the parameter to the appropriate frame in `gui/frames/`
2. Update `get_values()` and `set_values()` methods
3. Update `_get_all_values()` and `_set_all_values()` in `app.py`
4. Update `_build_config()` in `app.py` to include in Config object

### Adding a New Frame

1. Create new file in `gui/frames/`
2. Inherit from `ctk.CTkFrame`
3. Implement `get_values()` and `set_values()` methods
4. Export from `gui/frames/__init__.py`
5. Add to sidebar in `app.py._create_sidebar()`

### Adding Menu Items

1. Update `gui.py` to add new menu commands
2. Add keyboard shortcuts with `root.bind()`
3. Implement handler methods in `CoverflowApp`

## Mode-Dependent UI

The perspective slider is disabled when flat mode is selected because perspective has no effect in flat mode. This is implemented via:

1. `LayoutFrame.on_mode_change` callback fires when mode changes
2. `app.py._on_mode_change()` receives the mode
3. Calls `transform_frame.set_perspective_enabled(mode == "arc")`
4. `LabeledSlider.set_enabled()` enables/disables the slider and entry

To add more mode-dependent behavior, extend `_on_mode_change()` in `app.py`.
