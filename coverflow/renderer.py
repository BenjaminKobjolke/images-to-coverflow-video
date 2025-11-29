"""Coverflow frame rendering."""

from typing import List

import cv2
import numpy as np

from .transforms import ImageTransformer


class CoverflowRenderer:
    """Renders coverflow frames."""

    def __init__(self, width: int, height: int):
        """Initialize the renderer.

        Args:
            width: Canvas width.
            height: Canvas height.
        """
        self.width = width
        self.height = height
        self.transformer = ImageTransformer()
        self.visible_range = 3  # Show 3 images on each side

    def _create_background(self) -> np.ndarray:
        """Create a gradient background.

        Returns:
            Background canvas with gradient.
        """
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Create gradient background (dark gray to black)
        for y in range(self.height):
            intensity = int(40 * (1 - y / self.height))
            canvas[y, :] = [intensity, intensity, intensity]

        return canvas

    def render_frame(
        self, images: List[np.ndarray], center_idx: int, offset: float
    ) -> np.ndarray:
        """Render a single coverflow frame.

        Args:
            images: List of images.
            center_idx: Index of the center image.
            offset: Animation offset from -1.0 to 1.0 for transitions.

        Returns:
            Rendered frame as numpy array.
        """
        canvas = self._create_background()

        # Collect images to render with their z-order (depth)
        to_render = []

        for i in range(-self.visible_range, self.visible_range + 1):
            img_idx = center_idx + i
            if 0 <= img_idx < len(images):
                # Calculate position with offset
                position = i - offset

                # Get depth for z-ordering (center = highest z)
                depth = abs(position)

                to_render.append((depth, position, images[img_idx]))

        # Sort by depth (render far images first, center last)
        to_render.sort(key=lambda x: -x[0])

        # Maximum image size
        max_img_width = int(self.width * 0.5)
        max_img_height = int(self.height * 0.6)

        # Render each image
        for depth, position, img_cv in to_render:
            # Resize image to fit
            img_resized = self.transformer.resize_to_fit(
                img_cv, max_img_width, max_img_height
            )

            # Convert to BGRA for alpha blending
            if img_resized.shape[2] == 3:
                img_rgba = cv2.cvtColor(img_resized, cv2.COLOR_BGR2BGRA)
            else:
                img_rgba = img_resized

            # Apply perspective transform
            transformed, x_pos, y_pos = self.transformer.apply_perspective(
                img_rgba, position, self.width, self.height
            )

            if transformed is not None:
                # Adjust y position to be slightly above center
                y_pos = int(y_pos - self.height * 0.05)

                # Blend onto canvas
                canvas = self.transformer.blend_onto_canvas(
                    canvas, transformed, x_pos, y_pos
                )

                # Add reflection
                reflection = self.transformer.create_reflection(transformed, alpha=0.2)
                refl_y = y_pos + transformed.shape[0] + 5
                canvas = self.transformer.blend_onto_canvas(
                    canvas, reflection, x_pos, refl_y
                )

        return canvas
