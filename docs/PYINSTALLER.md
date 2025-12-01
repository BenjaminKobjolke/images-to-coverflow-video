# PyInstaller Build Notes

This document covers known issues and solutions when building the executable with PyInstaller.

## Build Command

The application is compiled using `compile_exe.bat`:

```batch
@echo off
call activate_environment.bat
call pyinstaller --name CoverflowVideoGenerator --onefile --windowed --copy-metadata imageio --copy-metadata imageio-ffmpeg --collect-data imageio_ffmpeg gui.py
pause
```

## Known Issues and Solutions

### 1. ImageIO Metadata Error

**Error:**
```
importlib.metadata.PackageNotFoundError: No package metadata was found for imageio
```

**Cause:**
`imageio` uses `importlib.metadata.version()` to read its version at startup. PyInstaller doesn't include package metadata by default, causing this error at runtime.

**Solution:**
Add these flags to the PyInstaller command:
- `--copy-metadata imageio` - Copies imageio's METADATA file from dist-info
- `--copy-metadata imageio-ffmpeg` - Copies imageio-ffmpeg's metadata

### 2. Config File Not Found

**Error:**
```
[Errno 2] No such file or directory: 'C:\\Users\\...\\AppData\\Local\\Temp\\_MEI...\\gui\\config.json'
```

**Cause:**
Code using `Path(__file__).parent` to locate config files will point to PyInstaller's temp extraction directory, which doesn't contain the config and is not writable.

**Solution:**
Store user settings in AppData instead of relative to source files. The `gui/settings.py` now uses:
- Windows: `%APPDATA%\CoverflowVideoGenerator\config.json`
- Other: `~/.config/CoverflowVideoGenerator/config.json`

**General Rule:**
Never use `__file__` for user-writable config files in PyInstaller apps. Use platform-appropriate locations like AppData.

### 3. FFmpeg Binary Missing

**Error:**
Video generation fails or FFmpeg codec errors occur.

**Cause:**
`imageio-ffmpeg` bundles its own FFmpeg binary, but PyInstaller doesn't include it automatically.

**Solution:**
Add this flag to the PyInstaller command:
- `--collect-data imageio_ffmpeg` - Includes the bundled FFmpeg binary

## PyInstaller Flag Reference

| Flag | Purpose |
|------|---------|
| `--onefile` | Bundle everything into a single executable |
| `--windowed` | Hide the console window (GUI app) |
| `--copy-metadata <pkg>` | Include package metadata for importlib.metadata |
| `--collect-data <pkg>` | Include package data files (non-Python files) |
| `--hidden-import <pkg>` | Force include a module not detected by analysis |

## Troubleshooting Future Issues

If new import errors occur after adding dependencies:

1. **ModuleNotFoundError**: Add `--hidden-import <module_name>`
2. **PackageNotFoundError**: Add `--copy-metadata <package_name>`
3. **Missing data files**: Add `--collect-data <package_name>`

To debug, run the exe from command line to see the full traceback:
```cmd
dist\CoverflowVideoGenerator.exe
```
