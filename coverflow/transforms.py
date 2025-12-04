"""Image transformation functions for coverflow effect."""

from typing import Optional, Tuple

import cv2
import numpy as np

from .utils import apply_decay_curve, apply_increase_curve


class ImageTransformer:
    """Handles image transformations for coverflow effect."""

    # Class-level cache for perspective transform matrices
    _perspective_cache: dict = {}

    @staticmethod
    def resize_to_fit(img: np.ndarray, max_width: int, max_height: int) -> np.ndarray:
        """Resize image to fit within bounds while maintaining aspect ratio.

        Uses INTER_LINEAR for speed during pre-scaling (good quality/speed balance).

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
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    @staticmethod
    def apply_perspective(
        img: np.ndarray, angle: float, canvas_width: int, canvas_height: int,
        perspective: float = 0.3, side_scale: float = 0.3, spacing: float = 0.35,
        mode: str = "arc", side_blur: float = 0.0, side_alpha: float = 1.0,
        side_scale_curve: str = "exponential", side_blur_curve: str = "linear",
        side_alpha_curve: str = "exponential",
        side_scale_start: int = 1, side_blur_start: int = 1, side_alpha_start: int = 1
    ) -> Tuple[Optional[np.ndarray], int, int]:
        """Apply a 3D perspective transform to simulate coverflow effect.

        Uses warpPerspective to transform the entire image content, simulating
        a page rotated around its vertical axis.

        Args:
            img: Input image.
            angle: Position angle from -1.0 (left) to 0.0 (center) to 1.0 (right).
            canvas_width: Width of the target canvas.
            canvas_height: Height of the target canvas.
            perspective: Amount of perspective distortion (0 = none, default: 0.3).
            side_scale: How much side images shrink (0 = same size, default: 0.3).
            spacing: Horizontal spacing between images (default: 0.35).
            mode: Layout mode - 'arc' (circular) or 'flat' (straight row).
            side_blur: Blur amount for side images (0 = no blur, higher = more blur).
            side_alpha: Opacity for side images (1.0 = fully visible, lower = fades).
            side_scale_curve: Curve type for side_scale effect.
            side_blur_curve: Curve type for side_blur effect.
            side_alpha_curve: Curve type for side_alpha effect.
            side_scale_start: Position where scale effect begins (1 = immediate).
            side_blur_start: Position where blur effect begins (1 = immediate).
            side_alpha_start: Position where alpha effect begins (1 = immediate).

        Returns:
            Tuple of (transformed image or None, x_offset, y_offset).
        """
        h, w = img.shape[:2]
        abs_angle = abs(angle)

        # Position scale always uses exponential (for consistent spacing)
        position_scale = side_scale ** abs_angle if side_scale > 0 else 1.0

        # Calculate effective angle for scale (offset by start index)
        effective_scale_angle = max(0, abs_angle - (side_scale_start - 1))

        # Visual scale uses selected curve (for image sizing)
        scale = apply_decay_curve(side_scale, effective_scale_angle, side_scale_curve) if side_scale > 0 else 1.0

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

        # Apply blur if configured using selected curve (increase: 0 at center)
        # Calculate effective angle for blur (offset by start index)
        effective_blur_angle = max(0, abs_angle - (side_blur_start - 1))
        if side_blur > 0 and effective_blur_angle > 0.01:
            blur_amount = apply_increase_curve(side_blur, effective_blur_angle, side_blur_curve)
            ksize = int(blur_amount) * 2 + 1
            if ksize > 1:
                img_scaled = cv2.GaussianBlur(img_scaled, (ksize, ksize), blur_amount)

        # Apply alpha fade if configured using selected curve (decay: 1.0 at center)
        # Calculate effective angle for alpha (offset by start index)
        effective_alpha_angle = max(0, abs_angle - (side_alpha_start - 1))
        if side_alpha < 1.0 and effective_alpha_angle > 0.01:
            alpha_factor = apply_decay_curve(side_alpha, effective_alpha_angle, side_alpha_curve)
            img_scaled[:, :, 3] = (img_scaled[:, :, 3] * alpha_factor).astype(np.uint8)

        # For center image, no perspective needed
        if abs_angle < 0.01:
            x_offset = int((canvas_width - new_w) / 2)
            y_offset = int((canvas_height - new_h) / 2)
            return img_scaled, x_offset, y_offset

        # For flat mode: skip perspective distortion, just use scaled image
        # Calculate position to ensure consistent overlap between images
        if mode == "flat":
            if abs_angle < 0.01:
                x_offset = int((canvas_width - new_w) / 2)
            else:
                # Estimate center image width (use position_scale for consistent spacing)
                center_width = w * position_scale / position_scale  # = w (center width)

                # k factor for overlap calculation
                # spacing = fraction NOT overlapping (0.1 = 10% gap, 90% overlap)
                k = 0.5 * (1 - side_scale) + spacing * side_scale

                # Displacement using geometric series sum (use position_scale for consistent spacing)
                if side_scale < 1.0:
                    displacement = w * k * (1 - position_scale) / (1 - side_scale)
                else:
                    displacement = w * k * abs_angle

                # Apply direction
                if angle > 0:
                    x_offset = int((canvas_width - new_w) / 2 + displacement)
                else:
                    x_offset = int((canvas_width - new_w) / 2 - displacement)

            y_offset = int((canvas_height - new_h) / 2)
            return img_scaled, x_offset, y_offset

        # Calculate perspective distortion for far edge
        # Far edge is smaller in BOTH dimensions (proportionally)
        perspective_amount = abs_angle * perspective  # How much smaller the far edge is
        h_inset = int(new_w * perspective_amount)  # Horizontal inset
        v_inset = int(new_h * perspective_amount / 2)  # Vertical inset (centered)

        # Cache key for perspective matrix (based on dimensions and insets)
        is_left = angle < 0
        cache_key = (new_w, new_h, h_inset, v_inset, is_left)

        # Check cache for pre-computed matrix
        if cache_key in ImageTransformer._perspective_cache:
            matrix = ImageTransformer._perspective_cache[cache_key]
        else:
            # Source points (original rectangle)
            pts1 = np.float32([
                [0, 0],           # top-left
                [new_w, 0],       # top-right
                [0, new_h],       # bottom-left
                [new_w, new_h]    # bottom-right
            ])

            if is_left:  # Left side - left edge is far (smaller)
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

            # Compute and cache perspective transform matrix
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            ImageTransformer._perspective_cache[cache_key] = matrix

        # Apply transform
        transformed = cv2.warpPerspective(
            img_scaled, matrix, (new_w, new_h),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0)
        )

        # Calculate position on canvas (arc mode - use position_scale for consistent spacing)
        x_offset = int((canvas_width - new_w) / 2 + angle * canvas_width * spacing * position_scale)
        y_offset = int((canvas_height - new_h) / 2)

        return transformed, x_offset, y_offset

    def create_reflection(
        self,
        img: np.ndarray,
        position: float,
        canvas_width: int,
        canvas_height: int,
        alpha: float = 0.3,
        perspective: float = 0.3,
        side_scale: float = 0.3,
        spacing: float = 0.35,
        mode: str = "arc",
        reflection_length: float = 0.5,
        side_blur: float = 0.0,
        side_alpha: float = 1.0,
        side_scale_curve: str = "exponential",
        side_blur_curve: str = "linear",
        side_alpha_curve: str = "exponential",
        side_scale_start: int = 1,
        side_blur_start: int = 1,
        side_alpha_start: int = 1,
    ) -> Tuple[Optional[np.ndarray], int, int]:
        """Create a reflection effect below the image.

        Applies perspective transform first, then flips vertically,
        ensuring the reflection has identical perspective to the original.

        Args:
            img: Input image (BGR or BGRA).
            position: Perspective position (-1.0 to 1.0).
            canvas_width: Canvas width for perspective calculation.
            canvas_height: Canvas height for perspective calculation.
            alpha: Overall opacity of the reflection (0.0 to 1.0).
            perspective: Amount of perspective distortion (0 = none, default: 0.3).
            side_scale: How much side images shrink (0 = same size, default: 0.3).
            spacing: Horizontal spacing between images (default: 0.35).
            mode: Layout mode - 'arc' (circular) or 'flat' (straight row).
            reflection_length: Fraction of image height to show in reflection (0.0-1.0).
            side_blur: Blur amount for side images (0 = no blur, higher = more blur).
            side_alpha: Opacity for side images (1.0 = fully visible, lower = fades).
            side_scale_curve: Curve type for side_scale effect.
            side_blur_curve: Curve type for side_blur effect.
            side_alpha_curve: Curve type for side_alpha effect.
            side_scale_start: Position where scale effect begins (1 = immediate).
            side_blur_start: Position where blur effect begins (1 = immediate).
            side_alpha_start: Position where alpha effect begins (1 = immediate).

        Returns:
            Tuple of (reflected image with gradient fade, x_offset, y_offset).
        """
        # Step 1: Apply perspective transform FIRST (normal mode)
        transformed, x_offset, y_offset = self.apply_perspective(
            img, position, canvas_width, canvas_height, perspective, side_scale, spacing, mode,
            side_blur, side_alpha, side_scale_curve, side_blur_curve, side_alpha_curve,
            side_scale_start, side_blur_start, side_alpha_start
        )

        if transformed is None:
            return None, 0, 0

        # Step 2: THEN flip the perspectived image vertically
        transformed = cv2.flip(transformed, 0)

        h, w = transformed.shape[:2]

        # Step 3: Crop to reflection_length (top portion of flipped = bottom of original)
        crop_h = max(1, int(h * reflection_length))
        transformed = transformed[:crop_h, :]
        h = crop_h

        # Step 4: Apply gradient fade to alpha channel (broadcasting handles width)
        gradient = np.linspace(1.0, 0, h, dtype=np.float32).reshape(-1, 1)

        if transformed.shape[2] == 4:
            # For BGRA: keep RGB intact, apply gradient to alpha only
            rgb = transformed[:, :, :3]
            alpha_channel = transformed[:, :, 3].astype(np.float32)
            # Broadcasting: gradient (h,1) * alpha_channel (h,w) works automatically
            alpha_channel = alpha_channel * gradient * alpha
            transformed = np.dstack([rgb, alpha_channel.astype(np.uint8)])
        else:
            # For BGR: convert to BGRA and apply gradient to alpha
            alpha_channel = (gradient * alpha * 255).astype(np.uint8)
            # Broadcast to full width
            alpha_channel = np.broadcast_to(alpha_channel, (h, w)).copy()
            transformed = np.dstack([transformed, alpha_channel])

        return transformed, x_offset, y_offset

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
