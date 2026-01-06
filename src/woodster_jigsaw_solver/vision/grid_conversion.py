from typing import List, Tuple

import cv2
import numpy as np
from cv2.typing import MatLike

from woodster_jigsaw_solver.models.puzzle_piece import PuzzlePiece


def contour_to_puzzle_piece(contour: MatLike, unit_length: float) -> PuzzlePiece:
    points = contour.reshape(-1, 2)

    min_x = int(np.min(points[:, 0]))
    min_y = int(np.min(points[:, 1]))
    max_x = int(np.max(points[:, 0]))
    max_y = int(np.max(points[:, 1]))

    width = max_x - min_x
    height = max_y - min_y

    num_cols = int(np.round(width / unit_length))
    num_rows = int(np.round(height / unit_length))

    binary_matrix: List[List[int]] = [[0] * num_cols for _ in range(num_rows)]

    for row in range(num_rows):
        for col in range(num_cols):
            center_x = int((col + 0.5) * unit_length)
            center_y = int((row + 0.5) * unit_length)

            inside = cv2.pointPolygonTest(
                contour, (center_x + min_x, center_y + min_y), False
            )

            if inside >= 0:
                binary_matrix[row][col] = 1

    coordinates: List[Tuple[int, int]] = []
    for row in range(num_rows):
        for col in range(num_cols):
            if binary_matrix[row][col] == 1:
                coordinates.append((col, row))

    return PuzzlePiece(coordinates)
