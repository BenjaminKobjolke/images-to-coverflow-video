"""Coverflow frame rendering."""

from typing import List, Optional

import cv2
import numpy as np

from .config import Config
from .transforms import ImageTransformer


def parse_hex_color(hex_color: str) -> tuple:
    """Parse hex color string to BGR tuple for OpenCV.

    Args:
        hex_color: Hex color string like "#FF5500" or "FF5500".

    Returns:
        BGR tuple like (0, 85, 255).
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)  # BGR for OpenCV


class CoverflowRenderer:
    """Renders coverflow frames."""

    def __init__(self, config: Config):
        """Initialize the renderer.

        Args:
            config: Video generation configuration.
        """
        self.config = config
        self.transformer = ImageTransformer()
        self.background_image = self._load_background(config.background)

    def _load_background(self, path: Optional[str]) -> Optional[np.ndarray]:
        """Load and resize background image.

        Args:
            path: Path to background image file.

        Returns:
            Resized background image or None.
        """
        if not path:
            return None

        # Load with IMREAD_UNCHANGED to preserve alpha channel for transparency
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Warning: Could not load background image '{path}'")
            return None

        # Resize to fit canvas (cover mode - fill entire canvas)
        img_h, img_w = img.shape[:2]
        scale = max(self.config.width / img_w, self.config.height / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        # Center crop to canvas size
        x_offset = (new_w - self.config.width) // 2
        y_offset = (new_h - self.config.height) // 2
        img_cropped = img_resized[y_offset:y_offset + self.config.height, x_offset:x_offset + self.config.width]

        return img_cropped

    def _create_background(self) -> np.ndarray:
        """Create background canvas.

        Returns:
            Background canvas (color, custom image, or gradient).
        """
        # Start with color or gradient as base
        if self.config.background_color:
            top_color = parse_hex_color(self.config.background_color)
            if self.config.background_color_bottom:
                # Two-color vertical gradient
                bottom_color = parse_hex_color(self.config.background_color_bottom)
                canvas = np.zeros((self.config.height, self.config.width, 3), dtype=np.uint8)
                for y in range(self.config.height):
                    t = y / self.config.height
                    color = [int(top_color[i] * (1 - t) + bottom_color[i] * t) for i in range(3)]
                    canvas[y, :] = color
            else:
                # Solid color
                canvas = np.full((self.config.height, self.config.width, 3), top_color, dtype=np.uint8)
        else:
            # Default: gradient background (dark gray to black)
            canvas = np.zeros((self.config.height, self.config.width, 3), dtype=np.uint8)
            for y in range(self.config.height):
                intensity = int(40 * (1 - y / self.config.height))
                canvas[y, :] = [intensity, intensity, intensity]

        # Overlay background image if exists
        if self.background_image is not None:
            # Blend with alpha if BGRA, else just copy
            if len(self.background_image.shape) == 3 and self.background_image.shape[2] == 4:
                alpha = self.background_image[:, :, 3:4] / 255.0
                rgb = self.background_image[:, :, :3]
                canvas = (rgb * alpha + canvas * (1 - alpha)).astype(np.uint8)
            else:
                canvas = self.background_image.copy()

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

        for i in range(-self.config.visible_range, self.config.visible_range + 1):
            img_idx = center_idx + i

            # Wrap around if repeat is enabled
            if self.config.repeat:
                img_idx = img_idx % len(images)

            if 0 <= img_idx < len(images):
                # Calculate position with offset
                position = i - offset

                # Get depth for z-ordering (center = highest z)
                depth = abs(position)

                to_render.append((depth, position, images[img_idx]))

        # Sort by depth (render far images first, center last)
        to_render.sort(key=lambda x: -x[0])

        # Maximum image size
        max_img_width = int(self.config.width * self.config.image_scale)
        max_img_height = int(self.config.height * self.config.image_scale)

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
                img_rgba, position, self.config.width, self.config.height,
                self.config.perspective, self.config.side_scale, self.config.spacing,
                self.config.mode, self.config.side_blur, self.config.side_alpha,
                self.config.side_scale_curve, self.config.side_blur_curve, self.config.side_alpha_curve,
                self.config.side_scale_start, self.config.side_blur_start, self.config.side_alpha_start
            )

            if transformed is not None:
                # Calculate base y position from image_y setting
                base_y = int(self.config.height * self.config.image_y - transformed.shape[0] / 2)

                # Apply alignment adjustment
                if self.config.alignment == "bottom":
                    y_pos = int(base_y + transformed.shape[0] / 2)
                elif self.config.alignment == "top":
                    y_pos = int(base_y - transformed.shape[0] / 2)
                else:  # center (default)
                    y_pos = base_y

                # Blend onto canvas
                canvas = self.transformer.blend_onto_canvas(
                    canvas, transformed, x_pos, y_pos
                )

                # Add reflection if enabled
                if self.config.reflection > 0:
                    reflection, refl_x, _ = self.transformer.create_reflection(
                        img_rgba, position, self.config.width, self.config.height,
                        alpha=self.config.reflection, perspective=self.config.perspective,
                        side_scale=self.config.side_scale, spacing=self.config.spacing,
                        mode=self.config.mode, reflection_length=self.config.reflection_length,
                        side_blur=self.config.side_blur, side_alpha=self.config.side_alpha,
                        side_scale_curve=self.config.side_scale_curve,
                        side_blur_curve=self.config.side_blur_curve,
                        side_alpha_curve=self.config.side_alpha_curve,
                        side_scale_start=self.config.side_scale_start,
                        side_blur_start=self.config.side_blur_start,
                        side_alpha_start=self.config.side_alpha_start,
                    )
                    if reflection is not None:
                        refl_y = y_pos + transformed.shape[0] + 5
                        canvas = self.transformer.blend_onto_canvas(
                            canvas, reflection, refl_x, refl_y
                        )

        return canvas
