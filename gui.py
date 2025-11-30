#!/usr/bin/env python3
"""
Coverflow Video Generator - GUI Application

A graphical interface for creating coverflow-style videos from image sequences.
"""

import tkinter as tk
import customtkinter as ctk

from gui import CoverflowApp
from gui.settings import load_settings


def main():
    """Run the GUI application."""
    # Load saved settings and set appearance mode
    settings = load_settings()
    ctk.set_appearance_mode(settings.get("theme", "Dark"))
    ctk.set_default_color_theme("blue")

    # Create main window
    root = ctk.CTk()
    root.title("Coverflow Video Generator")
    root.geometry("1200x800")
    root.minsize(900, 600)

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

    # Run the application
    root.mainloop()


if __name__ == "__main__":
    main()
