# Interface Architecture

This document describes the GUI architecture to help with future UI changes.

## Font System

All fonts are managed through `gui/fonts.py`:

```python
from gui.fonts import get_font

# Normal text
label = ctk.CTkLabel(parent, text="Label", font=get_font())

# Bold headers (same size)
title = ctk.CTkLabel(parent, text="Title", font=get_font(weight="bold"))

# Larger text (+2px from base)
big_label = ctk.CTkLabel(parent, text="Big", font=get_font(size_offset=2, weight="bold"))

# Smaller text (-3px from base)
small_label = ctk.CTkLabel(parent, text="Small", font=get_font(size_offset=-3))
```

**Important:** Always use `get_font()` for any `CTkLabel`, `CTkEntry`, or `CTkButton`. The base font size is configurable via Settings > Interface > Font Size.

## File Structure

```
gui/
├── __init__.py          # Exports CoverflowApp
├── app.py               # Main application frame
├── fonts.py             # Font utility (get_font)
├── settings.py          # Settings persistence (AppData)
├── projects.py          # Project file management
├── dialogs/
│   ├── __init__.py
│   └── interface_settings.py   # Settings dialog
├── frames/
│   ├── __init__.py
│   ├── source_frame.py      # Image folder selection
│   ├── video_frame.py       # Video output settings
│   ├── timing_frame.py      # Transition/hold timing
│   ├── layout_frame.py      # Mode, alignment, spacing
│   ├── transform_frame.py   # 3D perspective settings
│   ├── image_frame.py       # Image scale/position
│   ├── effects_frame.py     # Background, reflection
│   └── preview_frame.py     # Preview display + controls
└── widgets/
    ├── __init__.py
    ├── labeled_entry.py     # Entry with label + validation
    ├── labeled_slider.py    # Slider with label + entry
    ├── file_picker.py       # File/folder picker widgets
    ├── range_slider.py      # Dual-handle range slider
    ├── progress_dialog.py   # Video generation progress
    └── success_dialog.py    # Generation complete dialog
```

## Main Entry Point

`gui.py` - Creates the main window and menu bar:
- Loads settings from AppData
- Creates `CoverflowApp` frame
- Sets up File/Project/Settings menus
- Handles window geometry persistence

## Reusable Widgets

### LabeledEntry (`gui/widgets/labeled_entry.py`)
Numeric entry with label and validation.
```python
entry = LabeledEntry(parent, label="Width", default=800, min_value=100, max_value=4000, is_int=True)
value = entry.get()
entry.set(1920)
```

### LabeledSlider (`gui/widgets/labeled_slider.py`)
Slider with label and editable value field.
```python
slider = LabeledSlider(parent, label="Scale", from_=0.1, to=1.0, default=0.6, decimal_places=2)
value = slider.get()
slider.set(0.8)
```

### FilePicker / FolderPicker (`gui/widgets/file_picker.py`)
File/folder selection with browse button.
```python
picker = FilePicker(parent, label="Output", filetypes=(("MP4", "*.mp4"),), save_mode=True)
picker = FolderPicker(parent, label="Source", command=on_change)
path = picker.get()
```

### RangeSlider (`gui/widgets/range_slider.py`)
Dual-handle slider for selecting a range.
```python
slider = RangeSlider(parent, from_=0, to=100, command=on_change)
start, end = slider.get()
```

## Frame Pattern

Each settings frame follows this pattern:

```python
class ExampleFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Title (bold)
        self.title_label = ctk.CTkLabel(
            self, text="Example", font=get_font(weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Widgets
        self.some_slider = LabeledSlider(self, label="Setting", ...)
        self.some_slider.pack(fill="x", padx=10, pady=2)

    def get_values(self) -> dict:
        return {"setting": self.some_slider.get()}

    def set_values(self, values: dict):
        if "setting" in values:
            self.some_slider.set(values["setting"])
```

## Settings Storage

Settings are stored in JSON at:
- **Windows:** `%APPDATA%\CoverflowVideoGenerator\config.json`
- **Linux/Mac:** `~/.config/CoverflowVideoGenerator/config.json`

Current settings:
```python
DEFAULTS = {
    "theme": "Dark",           # "Dark" or "Light"
    "sidebar_columns": 1,      # 1 or 2
    "font_size": 14,           # 14-24
    "last_project": None,      # Last opened project path
    "recent_projects": [],     # List of recent project paths (max 10)
    "window_width": 1200,
    "window_height": 800,
    "window_x": None,
    "window_y": None,
    "window_maximized": False,
}
```

## Menu Structure

```
File
├── New Project (Ctrl+N)
├── Open Project... (Ctrl+O)
├── Recent Projects ►
│   └── (dynamic list)
├── ─────────────
├── Save Project (Ctrl+S)
├── Save Project As... (Ctrl+Shift+S)
├── ─────────────
└── Exit (Alt+F4)

Project
└── Statistics

Settings
└── Interface...
```

## Adding a New Setting

1. Add default to `gui/settings.py` DEFAULTS dict
2. Add UI control to appropriate frame or dialog
3. Update `get_values()` / `set_values()` methods
4. Use `load_settings()` / `save_settings()` for persistence

## Adding a New Frame

1. Create `gui/frames/new_frame.py` following the frame pattern
2. Export from `gui/frames/__init__.py`
3. Import and instantiate in `gui/app.py`
4. Add to `_create_sidebar_1col()` and `_create_sidebar_2col()`
5. Update `_get_all_values()` and `_set_all_values()` in app.py

## Styling Notes

- Use `fg_color="transparent"` for container frames
- Use `padx=10, pady=2` for consistent widget spacing
- Labels use `width=120, anchor="w"` for alignment
- Always use `get_font()` for text elements
- Section titles use `get_font(weight="bold")`
