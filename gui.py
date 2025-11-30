#!/usr/bin/env python3
"""
Coverflow Video Generator - GUI Application

A graphical interface for creating coverflow-style videos from image sequences.
"""

import tkinter as tk
import customtkinter as ctk

from gui import CoverflowApp
from gui.settings import load_settings, save_settings


def main():
    """Run the GUI application."""
    # Load saved settings and set appearance mode
    settings = load_settings()
    ctk.set_appearance_mode(settings.get("theme", "Dark"))
    ctk.set_default_color_theme("blue")

    # Create main window
    root = ctk.CTk()
    root.title("Coverflow Video Generator")
    root.minsize(900, 600)

    # Restore window geometry
    width = settings.get("window_width", 1200)
    height = settings.get("window_height", 800)
    x = settings.get("window_x")
    y = settings.get("window_y")

    # Validate and apply geometry
    root.update_idletasks()  # Ensure window is created
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Ensure size is reasonable
    width = max(900, min(width, screen_width))
    height = max(600, min(height, screen_height))

    # Check if position is valid (at least 100px visible on screen)
    if x is not None and y is not None:
        min_visible = 100
        if (x + width < min_visible or x > screen_width - min_visible or
                y + height < min_visible or y > screen_height - min_visible):
            # Position out of bounds, center window
            x = None
            y = None

    if x is not None and y is not None:
        root.geometry(f"{width}x{height}+{x}+{y}")
    else:
        # Center on screen
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")

    # Restore maximized state if it was maximized
    if settings.get("window_maximized", False):
        root.state('zoomed')

    # Configure grid
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # Create the application
    sidebar_columns = settings.get("sidebar_columns", 1)
    app = CoverflowApp(root, sidebar_columns=sidebar_columns)
    app.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    # Create menu bar (using tkinter Menu, attached to root)
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New Project", command=app._on_new_project, accelerator="Ctrl+N")
    file_menu.add_command(label="Open Project...", command=app._on_open_project, accelerator="Ctrl+O")
    file_menu.add_separator()
    file_menu.add_command(label="Save Project", command=app._on_save_project, accelerator="Ctrl+S")
    file_menu.add_command(label="Save Project As...", command=app._on_save_project_as, accelerator="Ctrl+Shift+S")

    # Project menu
    project_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Project", menu=project_menu)
    project_menu.add_command(label="Statistics", command=app._on_statistics)

    # Settings menu
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Interface...", command=app._on_interface_settings)

    # Keyboard shortcuts
    root.bind("<Control-n>", lambda e: app._on_new_project())
    root.bind("<Control-o>", lambda e: app._on_open_project())
    root.bind("<Control-s>", lambda e: app._on_save_project())
    root.bind("<Control-Shift-s>", lambda e: app._on_save_project_as())

    # Save window geometry on close
    def on_close():
        settings = load_settings()

        # Check if maximized (Windows uses 'zoomed')
        is_maximized = root.state() == 'zoomed'
        settings["window_maximized"] = is_maximized

        # Only save geometry if not maximized (preserve normal window size)
        if not is_maximized:
            settings["window_width"] = root.winfo_width()
            settings["window_height"] = root.winfo_height()
            settings["window_x"] = root.winfo_x()
            settings["window_y"] = root.winfo_y()

        save_settings(settings)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Run the application
    root.mainloop()


if __name__ == "__main__":
    main()
