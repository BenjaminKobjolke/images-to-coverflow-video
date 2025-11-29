"""Image loading functionality for coverflow video generation."""

import sys
from pathlib import Path
from typing import List

import cv2
import numpy as np


class ImageLoader:
    """Loads images from a source directory."""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

    def __init__(self, source_dir: str):
        """Initialize the image loader.

        Args:
            source_dir: Path to directory containing images.
        """
        self.source_path = Path(source_dir)

    def load_paths(self) -> List[Path]:
        """Get list of image file paths from the source directory.

        Returns:
            Sorted list of image file paths.

        Raises:
            SystemExit: If source directory doesn't exist or contains no images.
        """
        if not self.source_path.exists():
            print(f"Error: Source directory '{self.source_path}' does not exist")
            sys.exit(1)

        image_files = []
        for file in sorted(self.source_path.iterdir()):
            if file.suffix.lower() in self.SUPPORTED_FORMATS:
                image_files.append(file)

        if not image_files:
            print(f"Error: No images found in '{self.source_path}'")
            sys.exit(1)

        print(f"Found {len(image_files)} images")
        return image_files

    def load_images(self) -> List[np.ndarray]:
        """Load all images from the source directory into memory.

        Returns:
            List of images as numpy arrays in BGR format.

        Raises:
            SystemExit: If no valid images could be loaded.
        """
        image_paths = self.load_paths()

        print("Loading images...")
        images_data = []
        for img_path in image_paths:
            img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
            if img is not None:
                # Ensure BGR format
                if len(img.shape) == 2:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                elif img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                images_data.append(img)
            else:
                print(f"Warning: Could not load {img_path}")

        if len(images_data) < 1:
            print("Error: No valid images loaded")
            sys.exit(1)

        print(f"Loaded {len(images_data)} images")
        return images_data
