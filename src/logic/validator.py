"""Validation logic for polyomino pieces and puzzles."""

from __future__ import annotations

from typing import List, Set, Tuple


class ValidationError:
    """Represents a validation error.

    Attributes:
        error_type: Type of validation error
        message: Human-readable error message
        context: Additional context (piece_id, position, etc.)
    """

    def __init__(
        self,
        error_type: str,
        message: str,
        context: dict | None = None,
    ) -> None:
        """Initialize a validation error.

        Args:
            error_type: Type of validation error
            message: Human-readable error message
            context: Additional context information
        """
        self.error_type = error_type
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        """Get string representation."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.error_type}: {self.message} ({context_str})"
        return f"{self.error_type}: {self.message}"

    def __eq__(self, other: object) -> bool:
        """Check equality with another error."""
        if not isinstance(other, ValidationError):
            return NotImplemented
        return (
            self.error_type == other.error_type
            and self.message == other.message
            and self.context == other.context
        )


def validate_piece_shape(shape: Set[Tuple[int, int]]) -> List[ValidationError]:
    """Validate that a shape is a valid polyomino.

    Args:
        shape: Set of (row, col) coordinates

    Returns:
        List of validation errors (empty if valid)
    """
    errors: List[ValidationError] = []

    # Check non-empty
    if not shape:
        errors.append(
            ValidationError(
                "EMPTY_SHAPE",
                "Shape cannot be empty",
                {"shape_size": 0},
            )
        )
        return errors

    # Check contiguity
    if not is_contiguous(shape):
        errors.append(
            ValidationError(
                "NON_CONTIGUOUS",
                "Shape must be contiguous (all cells connected)",
                {"shape_size": len(shape)},
            )
        )

    return errors


def validate_piece_placement(
    piece_shape: Set[Tuple[int, int]],
    board_width: int,
    board_height: int,
    position: Tuple[int, int],
    occupied_cells: Set[Tuple[int, int]] | None = None,
) -> List[ValidationError]:
    """Validate that a piece can be placed at the specified position.

    Args:
        piece_shape: Set of (row, col) coordinates for the piece
        board_width: Board width in cells
        board_height: Board height in cells
        position: (row, col) position to place piece origin
        occupied_cells: Set of already occupied cell positions

    Returns:
        List of validation errors (empty if placement is valid)
    """
    errors: List[ValidationError] = []
    occupied = occupied_cells or set()

    # Check bounds for each cell
    for row_offset, col_offset in piece_shape:
        row = position[0] + row_offset
        col = position[1] + col_offset

        # Check board boundaries
        if not (0 <= row < board_height and 0 <= col < board_width):
            errors.append(
                ValidationError(
                    "OUT_OF_BOUNDS",
                    f"Cell ({row}, {col}) is outside board boundaries",
                    {
                        "row": row,
                        "col": col,
                        "board_width": board_width,
                        "board_height": board_height,
                    },
                )
            )

        # Check for overlap with existing pieces
        if (row, col) in occupied:
            errors.append(
                ValidationError(
                    "OVERLAP",
                    f"Cell ({row}, {col}) is already occupied",
                    {"position": (row, col)},
                )
            )

    return errors


def validate_puzzle_config(
    pieces: list,
    board_width: int,
    board_height: int,
) -> List[ValidationError]:
    """Validate a complete puzzle configuration.

    Args:
        pieces: List of puzzle pieces
        board_width: Board width in cells
        board_height: Board height in cells

    Returns:
        List of validation errors (empty if configuration is valid)
    """
    errors: List[ValidationError] = []

    # Check board dimensions
    if not (1 <= board_width <= 50):
        errors.append(
            ValidationError(
                "INVALID_BOARD_WIDTH",
                "Board width must be between 1 and 50",
                {"board_width": board_width},
            )
        )

    if not (1 <= board_height <= 50):
        errors.append(
            ValidationError(
                "INVALID_BOARD_HEIGHT",
                "Board height must be between 1 and 50",
                {"board_height": board_height},
            )
        )

    # Check at least one piece
    if not pieces:
        errors.append(
            ValidationError(
                "NO_PIECES",
                "At least one piece is required",
            )
        )
        return errors

    # Check unique piece names
    piece_names = []
    for piece in pieces:
        if not hasattr(piece, "name"):
            errors.append(
                ValidationError(
                    "MISSING_PIECE_NAME",
                    "Piece is missing name attribute",
                )
            )
            continue

        if piece.name in piece_names:
            errors.append(
                ValidationError(
                    "DUPLICATE_PIECE_NAME",
                    f"Duplicate piece name: {piece.name}",
                    {"piece_name": piece.name},
                )
            )
        piece_names.append(piece.name)

    # Validate each piece shape
    total_piece_area = 0
    for piece in pieces:
        if not hasattr(piece, "shape"):
            errors.append(
                ValidationError(
                    "MISSING_PIECE_SHAPE",
                    f"Piece {getattr(piece, 'name', 'unknown')} "
                    "is missing shape attribute",
                )
            )
            continue

        shape_errors = validate_piece_shape(piece.shape)
        errors.extend(shape_errors)
        total_piece_area += len(piece.shape)

    # Check area compatibility
    board_area = board_width * board_height
    if total_piece_area > board_area:
        errors.append(
            ValidationError(
                "AREA_MISMATCH",
                f"Total piece area ({total_piece_area}) "
                f"exceeds board area ({board_area})",
                {
                    "total_piece_area": total_piece_area,
                    "board_area": board_area,
                },
            )
        )

    return errors


def is_contiguous(shape: Set[Tuple[int, int]]) -> bool:
    """Check if all cells in shape are 4-directionally connected.

    Args:
        shape: Set of (row, col) coordinates

    Returns:
        True if shape is contiguous, False otherwise
    """
    if not shape:
        return True

    visited: Set[Tuple[int, int]] = set()
    stack: List[Tuple[int, int]] = [next(iter(shape))]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        row, col = current
        neighbors = [
            (row - 1, col),  # Up
            (row + 1, col),  # Down
            (row, col - 1),  # Left
            (row, col + 1),  # Right
        ]

        for neighbor in neighbors:
            if neighbor in shape and neighbor not in visited:
                stack.append(neighbor)

    return len(visited) == len(shape)


def find_connected_components(
    shape: Set[Tuple[int, int]],
) -> List[Set[Tuple[int, int]]]:
    """Find all connected components in a shape.

    Args:
        shape: Set of (row, col) coordinates

    Returns:
        List of connected component sets
    """
    if not shape:
        return []

    visited: Set[Tuple[int, int]] = set()
    components: List[Set[Tuple[int, int]]] = []

    for cell in shape:
        if cell in visited:
            continue

        # Start a new component
        component: Set[Tuple[int, int]] = set()
        stack: List[Tuple[int, int]] = [cell]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.add(current)

            row, col = current
            neighbors = [
                (row - 1, col),
                (row + 1, col),
                (row, col - 1),
                (row, col + 1),
            ]

            for neighbor in neighbors:
                if neighbor in shape and neighbor not in visited:
                    stack.append(neighbor)

        components.append(component)

    return components
