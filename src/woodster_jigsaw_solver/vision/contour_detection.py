from typing import List, Tuple

import cv2
import numpy as np
from cv2.typing import MatLike


def scan_puzzle_piece_contours(
    image: str | np.ndarray,
    min_area: int = 100,
    blur_kernel: Tuple[int, int] = (5, 5),
    canny_threshold1: int = 50,
    canny_threshold2: int = 150,
    approximation_epsilon: float = 0.01,
) -> List[MatLike]:
    if isinstance(image, str):
        img = cv2.imread(image)
        if img is None:
            raise ValueError(f"Unable to load image from path: {image}")
    else:
        img = image.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, blur_kernel, 0)
    edges = cv2.Canny(blurred, canny_threshold1, canny_threshold2)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    piece_contours: List[MatLike] = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        perimeter = cv2.arcLength(contour, True)
        epsilon = approximation_epsilon * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        piece_contours.append(approx)

    return piece_contours
