"""Image transformation functions for coverflow effect."""

from typing import Optional, Tuple

import cv2
import numpy as np


class ImageTransformer:
    """Handles image transformations for coverflow effect."""

    @staticmethod
    def resize_to_fit(img: np.ndarray, max_width: int, max_height: int) -> np.ndarray:
        """Resize image to fit within bounds while maintaining aspect ratio.

        Args:
            img: Input image.
            max_width: Maximum width.
            max_height: Maximum height.

        Returns:
            Resized image.
        """
        h, w = img.shape[:2]
        scale = min(max_width / w, max_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    @staticmethod
    def apply_perspective(
        img: np.ndarray, angle: float, canvas_width: int, canvas_height: int
    ) -> Tuple[Optional[np.ndarray], int, int]:
        """Apply a 3D perspective transform to simulate coverflow effect.

        Uses warpPerspective to transform the entire image content, simulating
        a page rotated around its vertical axis.

        Args:
            img: Input image.
            angle: Position angle from -1.0 (left) to 0.0 (center) to 1.0 (right).
            canvas_width: Width of the target canvas.
            canvas_height: Height of the target canvas.

        Returns:
            Tuple of (transformed image or None, x_offset, y_offset).
        """
        h, w = img.shape[:2]
        abs_angle = abs(angle)

        # Scale factor based on distance from center
        scale = 1.0 - abs_angle * 0.3

        # Scale both dimensions uniformly first
        new_w = int(w * scale)
        new_h = int(h * scale)

        if new_w <= 0 or new_h <= 0:
            return None, 0, 0

        # Resize image
        img_scaled = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        # Ensure BGRA format for alpha channel
        if img_scaled.shape[2] == 3:
            img_scaled = cv2.cvtColor(img_scaled, cv2.COLOR_BGR2BGRA)

        # For center image, no perspective needed
        if abs_angle < 0.01:
            x_offset = int((canvas_width - new_w) / 2)
            y_offset = int((canvas_height - new_h) / 2)
            return img_scaled, x_offset, y_offset

        # Calculate perspective distortion for far edge
        # Far edge is smaller in BOTH dimensions (proportionally)
        perspective_amount = abs_angle * 0.3  # How much smaller the far edge is
        h_inset = int(new_w * perspective_amount)  # Horizontal inset
        v_inset = int(new_h * perspective_amount / 2)  # Vertical inset (centered)

        # Source points (original rectangle)
        pts1 = np.float32([
            [0, 0],           # top-left
            [new_w, 0],       # top-right
            [0, new_h],       # bottom-left
            [new_w, new_h]    # bottom-right
        ])

        if angle < 0:  # Left side - left edge is far (smaller)
            pts2 = np.float32([
                [h_inset, v_inset],              # top-left: moves right and down
                [new_w, 0],                       # top-right: stays
                [h_inset, new_h - v_inset],      # bottom-left: moves right and up
                [new_w, new_h]                    # bottom-right: stays
            ])
        else:  # Right side - right edge is far (smaller)
            pts2 = np.float32([
                [0, 0],                           # top-left: stays
                [new_w - h_inset, v_inset],       # top-right: moves left and down
                [0, new_h],                       # bottom-left: stays
                [new_w - h_inset, new_h - v_inset]  # bottom-right: moves left and up
            ])

        # Get perspective transform matrix
        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        # Apply transform
        transformed = cv2.warpPerspective(
            img_scaled, matrix, (new_w, new_h),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0)
        )

        # Calculate position on canvas
        x_offset = int((canvas_width - new_w) / 2 + angle * canvas_width * 0.35)
        y_offset = int((canvas_height - new_h) / 2)

        return transformed, x_offset, y_offset

    @staticmethod
    def create_reflection(img: np.ndarray, alpha: float = 0.3) -> np.ndarray:
        """Create a reflection effect below the image.

        Args:
            img: Input image.
            alpha: Starting opacity of the reflection.

        Returns:
            Reflected image with gradient fade.
        """
        h, w = img.shape[:2]

        # Flip vertically
        reflected = cv2.flip(img, 0)

        # Create gradient mask for fade effect
        gradient = np.linspace(alpha, 0, h).reshape(-1, 1)
        gradient = np.tile(gradient, (1, w))

        if len(reflected.shape) == 3:
            gradient = np.dstack([gradient] * reflected.shape[2])

        # Apply gradient
        reflected = (reflected * gradient).astype(np.uint8)

        return reflected

    @staticmethod
    def blend_onto_canvas(
        canvas: np.ndarray, img: Optional[np.ndarray], x: int, y: int
    ) -> np.ndarray:
        """Blend an image onto the canvas at position (x, y) with alpha.

        Args:
            canvas: Target canvas.
            img: Image to blend (may be None).
            x: X position on canvas.
            y: Y position on canvas.

        Returns:
            Canvas with blended image.
        """
        if img is None:
            return canvas

        h, w = img.shape[:2]
        canvas_h, canvas_w = canvas.shape[:2]

        # Calculate visible region
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(canvas_w, x + w), min(canvas_h, y + h)

        if x1 >= x2 or y1 >= y2:
            return canvas

        # Calculate source region
        src_x1 = x1 - x
        src_y1 = y1 - y
        src_x2 = src_x1 + (x2 - x1)
        src_y2 = src_y1 + (y2 - y1)

        # Handle alpha blending if image has alpha channel
        if img.shape[2] == 4:
            alpha = img[src_y1:src_y2, src_x1:src_x2, 3:4] / 255.0
            rgb = img[src_y1:src_y2, src_x1:src_x2, :3]
            canvas_region = canvas[y1:y2, x1:x2]
            blended = (rgb * alpha + canvas_region * (1 - alpha)).astype(np.uint8)
            canvas[y1:y2, x1:x2] = blended
        else:
            canvas[y1:y2, x1:x2] = img[src_y1:src_y2, src_x1:src_x2]

        return canvas
