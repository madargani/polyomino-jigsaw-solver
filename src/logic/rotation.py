"""Rotation and flip operations for polyomino pieces."""

from __future__ import annotations

from typing import List, Set, Tuple


def rotate_shape(
    shape: Set[Tuple[int, int]], degrees: int = 90
) -> Set[Tuple[int, int]]:
    """Rotate a shape by specified degrees (90, 180, 270).

    Args:
        shape: Set of (row, col) coordinates
        degrees: Rotation angle in degrees (90, 180, or 270)

    Returns:
        Rotated shape coordinates

    Raises:
        ValueError: If degrees is not a multiple of 90
    """
    if degrees % 90 != 0:
        raise ValueError("Rotation must be a multiple of 90 degrees")

    # Normalize to 0-360
    degrees = degrees % 360

    if degrees == 0:
        return shape.copy()

    if degrees == 90:
        new_shape = {(col, -row) for row, col in shape}
    elif degrees == 180:
        new_shape = {(-row, -col) for row, col in shape}
    else:  # degrees == 270
        new_shape = {(-col, row) for row, col in shape}

    # Normalize to origin
    return _normalize_shape(new_shape)


def flip_shape(
    shape: Set[Tuple[int, int]], axis: str = "horizontal"
) -> Set[Tuple[int, int]]:
    """Flip (mirror) a shape along specified axis.

    Args:
        shape: Set of (row, col) coordinates
        axis: 'horizontal' or 'vertical'

    Returns:
        Flipped shape coordinates

    Raises:
        ValueError: If axis is not 'horizontal' or 'vertical'
    """
    if axis not in ("horizontal", "vertical"):
        raise ValueError("Axis must be 'horizontal' or 'vertical'")

    if axis == "horizontal":
        new_shape = {(row, -col) for row, col in shape}
    else:
        new_shape = {(-row, col) for row, col in shape}

    # Normalize to origin
    return _normalize_shape(new_shape)


def get_all_orientations(
    shape: Set[Tuple[int, int]],
) -> List[Set[Tuple[int, int]]]:
    """Generate all unique orientations of a shape.

    This includes all rotations (0, 90, 180, 270) and all flips.

    Args:
        shape: Set of (row, col) coordinates

    Returns:
        List of unique shape orientations
    """
    orientations: List[Set[Tuple[int, int]]] = []
    seen_shapes: Set[frozenset[Tuple[int, int]]] = set()

    for flip_axis in [None, "horizontal", "vertical"]:
        if flip_axis is None:
            base_shape = shape
        else:
            base_shape = flip_shape(shape, flip_axis)

        for degrees in [0, 90, 180, 270]:
            oriented = rotate_shape(base_shape, degrees)
            shape_key = frozenset(_normalize_shape(oriented))
            if shape_key not in seen_shapes:
                seen_shapes.add(shape_key)
                orientations.append(oriented)

    return orientations


def get_unique_rotations(shape: Set[Tuple[int, int]]) -> List[Set[Tuple[int, int]]]:
    """Generate unique rotations of a shape (no flips).

    Args:
        shape: Set of (row, col) coordinates

    Returns:
        List of unique rotations
    """
    rotations: List[Set[Tuple[int, int]]] = []
    seen_shapes: Set[frozenset[Tuple[int, int]]] = set()

    for degrees in [0, 90, 180, 270]:
        rotated = rotate_shape(shape, degrees)
        shape_key = frozenset(_normalize_shape(rotated))
        if shape_key not in seen_shapes:
            seen_shapes.add(shape_key)
            rotations.append(rotated)

    return rotations


def _normalize_shape(shape: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    """Normalize shape to origin (min row/col = 0, 0).

    Args:
        shape: Set of (row, col) coordinates

    Returns:
        Normalized shape coordinates
    """
    if not shape:
        return set()

    min_row = min(row for row, _ in shape)
    min_col = min(col for _, col in shape)
    return {(row - min_row, col - min_col) for row, col in shape}


def shape_to_string(shape: Set[Tuple[int, int]]) -> str:
    """Convert shape to string representation for debugging.

    Args:
        shape: Set of (row, col) coordinates

    Returns:
        String representation like "{(0,0), (0,1), (1,1)}"
    """
    return "{" + ", ".join(f"({r},{c})" for r, c in sorted(shape)) + "}"


def shape_from_string(shape_str: str) -> Set[Tuple[int, int]]:
    """Parse shape from string representation.

    Args:
        shape_str: String like "{(0,0), (0,1), (1,1)}" or "0,0 0,1 1,1"

    Returns:
        Set of (row, col) coordinates

    Raises:
        ValueError: If format is invalid
    """
    import re

    cleaned = shape_str.strip()
    if cleaned.startswith("{") and cleaned.endswith("}"):
        cleaned = cleaned[1:-1]

    if not cleaned.strip():
        return set()

    # Use regex to find all coordinate pairs like (0,1)
    coord_pattern = r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)"
    matches = re.findall(coord_pattern, cleaned)

    if not matches and "(" not in cleaned:
        # Try space-separated format: "0,0 0,1 1,1"
        parts = cleaned.split()
        shape: Set[Tuple[int, int]] = set()
        for part in parts:
            coords = part.split(",")
            if len(coords) == 2:
                try:
                    row = int(coords[0].strip())
                    col = int(coords[1].strip())
                    shape.add((row, col))
                except ValueError:
                    pass
        return shape

    shape: Set[Tuple[int, int]] = set()
    for match in matches:
        try:
            row = int(match[0])
            col = int(match[1])
            shape.add((row, col))
        except ValueError:
            raise ValueError(f"Invalid coordinate: ({match[0]}, {match[1]})")

    return shape
