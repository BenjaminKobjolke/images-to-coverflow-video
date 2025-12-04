# TODO: First Transition Feature (Completed)

## Completed
- [x] Add `first_transition` field to `coverflow/config.py`
- [x] Update total frames calculation in `coverflow/video_generator.py`
- [x] Update transition rendering loop to use `first_trans_frames` when `img_idx == 0`
- [x] Update preview mode frame lookup to handle first transition differently
- [x] Update `gui/workers/preview_worker.py` - `calculate_total_frames()` and frame lookup
- [x] Update `main.py` - DEFAULTS, CLI argument, print output, Config creation
- [x] Update `gui/frames/timing_frame.py` - first transition slider

## Feature Description
Allows setting a different duration for the first transition (image 1 → image 2) compared to subsequent transitions.

**Usage:**
- CLI: `--first-transition 1.0` (with `--transition 2.0` means first is 1s, rest are 2s)
- GUI: "First Trans." slider in Timing section (0 = use normal transition)

---

# TODO: Start Index for Side Effects (Completed)

## Completed
- [x] Add `side_scale_start`, `side_blur_start`, `side_alpha_start` fields to `coverflow/config.py`
- [x] Update `coverflow/transforms.py` - apply_perspective() and create_reflection() with effective angle calculations
- [x] Update `coverflow/renderer.py` - pass start index params to transform functions
- [x] Update `main.py` - DEFAULTS dict, CLI arguments, print output, Config creation
- [x] Update `gui/app.py` - defaults, _build_config()
- [x] Update `gui/frames/transform_frame.py` - entry widgets for start indices

## Feature Description
Adds a "start index" parameter for side_scale, side_blur, and side_alpha. This delays when the effect begins - e.g., start_index=2 means positions 0 and 1 are unaffected.

**Usage:**
- CLI: `--side-scale-start 2`, `--side-blur-start 2`, `--side-alpha-start 2`
- GUI: Entry fields next to each curve dropdown in the 3D Effect section

## Example with side_scale=0.7, start_index=2:
| Position | Current (start=1) | With start=2 |
|----------|-------------------|--------------|
| 0 (center) | 1.0 | 1.0 |
| 1 | 0.7 | 1.0 (no effect) |
| 2 | 0.49 | 0.7 (effect starts) |
| 3 | 0.34 | 0.49 |
