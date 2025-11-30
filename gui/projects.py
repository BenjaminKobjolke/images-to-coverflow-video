"""Project save/load functionality for GUI settings."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_projects_dir() -> Path:
    """Get the default directory for projects.

    Returns:
        Path to projects directory.
    """
    # Store projects next to the script
    base_dir = Path(__file__).parent.parent
    projects_dir = base_dir / "projects"
    projects_dir.mkdir(exist_ok=True)
    return projects_dir


def save_project(filepath: Path, name: str, settings: Dict[str, Any]) -> None:
    """Save project to JSON file.

    Args:
        filepath: Path to save the project file.
        name: Name of the project.
        settings: Dictionary of settings to save (ALL fields including paths).
    """
    project = {
        "project_name": name,
        "project_version": "1.0",
        "settings": settings,
    }

    with open(filepath, "w") as f:
        json.dump(project, f, indent=2)


def load_project(filepath: Path) -> Dict[str, Any]:
    """Load project from JSON file.

    Args:
        filepath: Path to the project file.

    Returns:
        Dictionary of settings.
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    return data.get("settings", {})


def get_project_name(filepath: Path) -> str:
    """Get the name of a project from its file.

    Args:
        filepath: Path to the project file.

    Returns:
        Project name or filename without extension.
    """
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return data.get("project_name", filepath.stem)
    except Exception:
        return filepath.stem


def list_projects(directory: Optional[Path] = None) -> List[Path]:
    """List all project files in a directory.

    Args:
        directory: Directory to search (defaults to projects dir).

    Returns:
        List of project file paths.
    """
    if directory is None:
        directory = get_projects_dir()

    if not directory.exists():
        return []

    return sorted(directory.glob("*.json"))


def create_default_projects():
    """Create default project files if they don't exist."""
    # No default projects - users create their own
    # Just ensure the directory exists
    get_projects_dir()
