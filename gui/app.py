"""Main application window for Coverflow Video Generator GUI."""

import os
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk

from coverflow import Config, ImageLoader

from .frames import (
    SourceFrame,
    VideoFrame,
    TimingFrame,
    LayoutFrame,
    TransformFrame,
    ImageFrame,
    EffectsFrame,
    PreviewFrame,
)
from .widgets import ProgressDialog
from .workers import PreviewWorker, VideoWorker
from .workers.preview_worker import calculate_total_frames
from .projects import (
    get_projects_dir,
    save_project,
    load_project,
    get_project_name,
    create_default_projects,
)
from .dialogs import InterfaceSettingsDialog


class CoverflowApp(ctk.CTkFrame):
    """Main application frame for Coverflow Video Generator."""

    def __init__(self, master, sidebar_columns: int = 1, **kwargs):
        """Initialize the application."""
        super().__init__(master, **kwargs)

        self.master = master
        self._sidebar_columns = sidebar_columns
        self._video_worker: Optional[VideoWorker] = None
        self._progress_dialog: Optional[ProgressDialog] = None
        self._selected_project_path: Optional[Path] = None

        # Create projects directory if needed
        create_default_projects()

        # Configure grid - wider sidebar for 2 columns
        sidebar_width = 660 if sidebar_columns == 2 else 350
        self.grid_columnconfigure(0, weight=0, minsize=sidebar_width)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar (scrollable)
        self._create_sidebar()

        # Create main panel
        self._create_main_panel()

        # Load default preset values
        self._load_default_values()

    def _create_sidebar(self):
        """Create the left sidebar with settings."""
        # Scrollable frame for settings
        sidebar_width = 630 if self._sidebar_columns == 2 else 330
        self.sidebar = ctk.CTkScrollableFrame(self, width=sidebar_width)
        self.sidebar.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        if self._sidebar_columns == 2:
            self._create_sidebar_2col()
        else:
            self._create_sidebar_1col()

    def _create_sidebar_1col(self):
        """Create sidebar frames in single column layout."""
        # Source frame
        self.source_frame = SourceFrame(
            self.sidebar, command=self._on_source_change
        )
        self.source_frame.pack(fill="x", pady=(0, 5))

        # Video settings
        self.video_frame = VideoFrame(self.sidebar)
        self.video_frame.pack(fill="x", pady=5)

        # Timing settings
        self.timing_frame = TimingFrame(self.sidebar)
        self.timing_frame.pack(fill="x", pady=5)

        # Layout settings
        self.layout_frame = LayoutFrame(
            self.sidebar, on_mode_change=self._on_mode_change
        )
        self.layout_frame.pack(fill="x", pady=5)

        # Transform settings
        self.transform_frame = TransformFrame(self.sidebar)
        self.transform_frame.pack(fill="x", pady=5)

        # Image settings
        self.image_frame = ImageFrame(self.sidebar)
        self.image_frame.pack(fill="x", pady=5)

        # Effects settings
        self.effects_frame = EffectsFrame(self.sidebar)
        self.effects_frame.pack(fill="x", pady=5)

    def _create_sidebar_2col(self):
        """Create sidebar frames in two column layout."""
        # Configure grid columns
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_columnconfigure(1, weight=1)

        # Create column containers
        col1 = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        col1.grid(row=0, column=0, sticky="new", padx=(0, 5))

        col2 = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        col2.grid(row=0, column=1, sticky="new", padx=(5, 0))

        # Column 1: Source, Video, Timing
        self.source_frame = SourceFrame(col1, command=self._on_source_change)
        self.source_frame.pack(fill="x", pady=(0, 5))

        self.video_frame = VideoFrame(col1)
        self.video_frame.pack(fill="x", pady=5)

        self.timing_frame = TimingFrame(col1)
        self.timing_frame.pack(fill="x", pady=5)

        # Column 2: 3D Effect, Image, Layout, Effects
        self.transform_frame = TransformFrame(col2)
        self.transform_frame.pack(fill="x", pady=(0, 5))

        self.image_frame = ImageFrame(col2)
        self.image_frame.pack(fill="x", pady=5)

        self.layout_frame = LayoutFrame(col2, on_mode_change=self._on_mode_change)
        self.layout_frame.pack(fill="x", pady=5)

        self.effects_frame = EffectsFrame(col2)
        self.effects_frame.pack(fill="x", pady=5)

    def _create_main_panel(self):
        """Create the main panel with preview and controls."""
        main_panel = ctk.CTkFrame(self)
        main_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        main_panel.grid_columnconfigure(0, weight=1)
        main_panel.grid_rowconfigure(0, weight=1)

        # Preview frame
        self.preview_frame = PreviewFrame(
            main_panel,
            on_refresh=self._on_preview_refresh,
            on_frame_change=self._on_frame_change,
        )
        self.preview_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Action buttons frame
        action_frame = ctk.CTkFrame(main_panel, fg_color="transparent")
        action_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)

        # Generate button (centered)
        self.generate_btn = ctk.CTkButton(
            action_frame,
            text="Generate Video",
            command=self._on_generate,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.generate_btn.grid(row=0, column=0, padx=5, sticky="ew")

    def _update_title(self):
        """Update window title with current project name."""
        if self._selected_project_path:
            name = get_project_name(self._selected_project_path)
            self.master.title(f"Coverflow Video Generator - {name}")
        else:
            self.master.title("Coverflow Video Generator")

    def _load_default_values(self):
        """Load default values into all frames."""
        self.video_frame.set_values({
            "width": 800,
            "height": 600,
            "fps": 30,
            "output": "output.mp4",
        })
        self.timing_frame.set_values({
            "transition": 2.0,
            "hold": 2.0,
        })
        self.layout_frame.set_values({
            "mode": "arc",
            "alignment": "center",
            "visible_range": 3,
            "spacing": 0.35,
        })
        self.transform_frame.set_values({
            "perspective": 0.3,
            "side_scale": 0.8,
        })
        self.image_frame.set_values({
            "image_scale": 0.6,
            "image_y": 0.5,
        })
        self.effects_frame.set_values({
            "reflection": 0.2,
            "reflection_length": 0.5,
            "repeat": False,
        })

    def _get_all_values(self) -> dict:
        """Get all settings values from all frames."""
        values = {}
        values["source"] = self.source_frame.get()
        values.update(self.video_frame.get_values())
        values.update(self.timing_frame.get_values())
        values.update(self.layout_frame.get_values())
        values.update(self.transform_frame.get_values())
        values.update(self.image_frame.get_values())
        values.update(self.effects_frame.get_values())
        return values

    def _set_all_values(self, values: dict):
        """Set all settings values in all frames."""
        if "source" in values:
            self.source_frame.set(values["source"])
        self.video_frame.set_values(values)
        self.timing_frame.set_values(values)
        self.layout_frame.set_values(values)
        self.transform_frame.set_values(values)
        self.image_frame.set_values(values)
        self.effects_frame.set_values(values)

    def _build_config(self) -> Optional[Config]:
        """Build a Config object from current settings."""
        values = self._get_all_values()

        if not values["source"]:
            messagebox.showerror("Error", "Please select a source folder.")
            return None

        if not os.path.isdir(values["source"]):
            messagebox.showerror("Error", "Source folder does not exist.")
            return None

        return Config(
            source=values["source"],
            width=values["width"],
            height=values["height"],
            transition=values["transition"],
            hold=values["hold"],
            fps=values["fps"],
            output=values["output"],
            background=values.get("background"),
            perspective=values["perspective"],
            side_scale=values["side_scale"],
            visible_range=values["visible_range"],
            spacing=values["spacing"],
            reflection=values["reflection"],
            reflection_length=values["reflection_length"],
            repeat=values["repeat"],
            mode=values["mode"],
            alignment=values["alignment"],
            image_scale=values["image_scale"],
            image_y=values["image_y"],
        )

    def _on_source_change(self, path: str):
        """Handle source folder change."""
        self._update_total_frames()

    def _on_mode_change(self, mode: str):
        """Handle layout mode change - enable/disable perspective for flat mode."""
        # Perspective has no effect in flat mode, so disable it
        self.transform_frame.set_perspective_enabled(mode == "arc")

    def _update_total_frames(self):
        """Update the total frames in the preview frame."""
        source = self.source_frame.get()
        if not source or not os.path.isdir(source):
            self.preview_frame.set_total_frames(100)
            return

        try:
            loader = ImageLoader(source)
            paths = loader.load_paths()
            num_images = len(paths)

            if num_images == 0:
                self.preview_frame.set_total_frames(100)
                return

            config = self._build_config()
            if config:
                total = calculate_total_frames(config, num_images)
                self.preview_frame.set_total_frames(total)
        except Exception:
            self.preview_frame.set_total_frames(100)

    def _on_preview_refresh(self):
        """Handle preview refresh button click."""
        config = self._build_config()
        if not config:
            return

        self.preview_frame.set_loading(True)
        frame_number = self.preview_frame.get_frame_number()

        worker = PreviewWorker(
            config,
            on_complete=self._on_preview_complete,
            frame_number=frame_number,
        )
        worker.start()

    def _on_preview_complete(self, image, error: Optional[str]):
        """Handle preview render completion."""
        # Schedule on main thread
        self.after(0, lambda: self._handle_preview_result(image, error))

    def _handle_preview_result(self, image, error: Optional[str]):
        """Handle preview result on main thread."""
        self.preview_frame.set_loading(False)

        if error:
            self.preview_frame.show_error(f"Error: {error}")
        elif image is not None:
            self.preview_frame.display_image(image)
            self._update_total_frames()

    def _on_frame_change(self, frame: int):
        """Handle frame slider change - auto refresh preview."""
        # Don't auto-refresh on every slider change (too slow)
        pass

    def _on_generate(self):
        """Handle generate video button click."""
        config = self._build_config()
        if not config:
            return

        # Create progress dialog
        self._progress_dialog = ProgressDialog(
            self.master,
            title="Generating Video",
            on_cancel=self._on_cancel_generation,
        )
        self._progress_dialog.set_status("Starting video generation...")

        # Create and start worker
        self._video_worker = VideoWorker(
            config,
            on_progress=self._on_generation_progress,
            on_complete=self._on_generation_complete,
        )
        self._video_worker.start()

    def _on_generation_progress(self, current: int, total: int):
        """Handle generation progress update."""
        self.after(0, lambda: self._update_progress(current, total))

    def _update_progress(self, current: int, total: int):
        """Update progress dialog on main thread."""
        if self._progress_dialog:
            progress = current / total if total > 0 else 0
            self._progress_dialog.set_progress(progress, current, total)
            self._progress_dialog.set_status("Generating video...")

    def _on_generation_complete(self, success: bool, error: Optional[str]):
        """Handle generation completion."""
        self.after(0, lambda: self._handle_generation_result(success, error))

    def _handle_generation_result(self, success: bool, error: Optional[str]):
        """Handle generation result on main thread."""
        if self._progress_dialog:
            self._progress_dialog.close()
            self._progress_dialog = None

        if success:
            output = self.video_frame.get_values()["output"]
            messagebox.showinfo("Success", f"Video saved to:\n{output}")
        elif error and "Cancelled" not in error:
            messagebox.showerror("Error", f"Video generation failed:\n{error}")

        self._video_worker = None

    def _on_cancel_generation(self):
        """Handle cancel button in progress dialog."""
        if self._video_worker:
            self._video_worker.cancel()

    def _on_statistics(self):
        """Handle statistics button click."""
        config = self._build_config()
        if not config:
            return

        try:
            loader = ImageLoader(config.source)
            paths = loader.load_paths()
            num_images = len(paths)

            if num_images == 0:
                messagebox.showinfo("Statistics", "No images found in source folder.")
                return

            total_frames = calculate_total_frames(config, num_images)
            duration = total_frames / config.fps

            stats = (
                f"Images: {num_images}\n"
                f"Total frames: {total_frames}\n"
                f"Duration: {duration:.2f} seconds\n"
                f"Resolution: {config.width}x{config.height}\n"
                f"FPS: {config.fps}"
            )
            messagebox.showinfo("Video Statistics", stats)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_interface_settings(self):
        """Open interface settings dialog."""
        InterfaceSettingsDialog(self.master)

    def _on_new_project(self):
        """Create a new project - reset to defaults and clear current project."""
        self._selected_project_path = None
        self._load_default_values()
        self.source_frame.set("")
        self._update_title()

    def _on_open_project(self):
        """Open a project file via file dialog."""
        filepath = filedialog.askopenfilename(
            title="Open Project",
            initialdir=get_projects_dir(),
            filetypes=(("Project files", "*.json"), ("All files", "*.*")),
        )

        if not filepath:
            return

        try:
            self._selected_project_path = Path(filepath)
            values = load_project(self._selected_project_path)
            self._set_all_values(values)
            self._update_title()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project:\n{e}")
            self._selected_project_path = None

    def _on_save_project(self):
        """Save current project. Use Save As if no project is open."""
        if self._selected_project_path is None:
            # No project open - use Save As
            self._on_save_project_as()
        else:
            # Project is open - save directly
            try:
                name = get_project_name(self._selected_project_path)
                values = self._get_all_values()
                save_project(self._selected_project_path, name, values)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save project:\n{e}")

    def _on_save_project_as(self):
        """Save project to a new file via file dialog."""
        filepath = filedialog.asksaveasfilename(
            title="Save Project As",
            initialdir=get_projects_dir(),
            defaultextension=".json",
            filetypes=(("Project files", "*.json"), ("All files", "*.*")),
        )

        if not filepath:
            return

        try:
            filepath = Path(filepath)
            name = filepath.stem  # Use filename as project name
            values = self._get_all_values()
            save_project(filepath, name, values)
            self._selected_project_path = filepath
            self._update_title()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project:\n{e}")
