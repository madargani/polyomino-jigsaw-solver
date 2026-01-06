from typing import List, Tuple

import cv2
import numpy as np
from cv2.typing import MatLike


def draw_contour(
    contour: MatLike,
    color: Tuple[int, int, int] = (0, 255, 0),
    background: Tuple[int, int, int] = (32, 32, 32),
    padding: int = 10,
) -> np.ndarray:
    min_x, min_y = np.min(contour, axis=0)[0]
    max_x, max_y = np.max(contour, axis=0)[0]

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    normalized_contour = contour - np.array([min_x, min_y])
    normalized_contour = normalized_contour + padding

    cropped_width = width + 2 * padding
    cropped_height = height + 2 * padding

    blank_img = np.full((cropped_height, cropped_width, 3), background, dtype=np.uint8)
    contour_reshaped = normalized_contour.reshape((-1, 1, 2))
    cv2.drawContours(blank_img, [contour_reshaped], -1, color, thickness=cv2.FILLED)

    return blank_img
