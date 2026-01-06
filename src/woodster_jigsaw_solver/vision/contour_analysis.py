import cv2
import numpy as np
from cv2.typing import MatLike


def find_contour_angle(contour: MatLike) -> float:
    sum_sin = 0.0
    sum_cos = 0.0

    for i in range(len(contour)):
        x1, y1 = contour[i][0]
        x2, y2 = contour[(i + 1) % len(contour)][0]

        dx = x2 - x1
        dy = y2 - y1
        length = (dx * dx + dy * dy) ** 0.5

        if length == 0:
            continue

        angle_rad = np.arctan2(dy, dx)
        angle_x4 = angle_rad * 4

        sum_sin += length * np.sin(angle_x4)
        sum_cos += length * np.cos(angle_x4)

    if sum_cos == 0 and sum_sin == 0:
        return 0.0

    avg_angle_x4 = np.arctan2(sum_sin, sum_cos)
    avg_angle = avg_angle_x4 / 4.0
    avg_angle_deg = np.degrees(avg_angle)

    return avg_angle_deg


def rotate_contour(contour: MatLike, angle_degrees: float) -> MatLike:
    M = cv2.moments(contour)
    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]
    centroid = np.array([cx, cy])

    points = contour.reshape(-1, 2)
    angle_rad = np.radians(angle_degrees)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)

    translated = points - centroid

    rotated = np.zeros_like(translated, dtype=np.float64)
    rotated[:, 0] = cos_a * translated[:, 0] - sin_a * translated[:, 1]
    rotated[:, 1] = sin_a * translated[:, 0] + cos_a * translated[:, 1]

    final = rotated + centroid

    return final.reshape(-1, 1, 2).astype(np.int32)


def find_unit_length(contour: MatLike, min_length: float = 5.0) -> float:
    points = contour.reshape(-1, 2)
    side_lengths = []

    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]

        length = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        if length >= min_length:
            side_lengths.append(length)

    if not side_lengths:
        return 0.0

    return min(side_lengths)
