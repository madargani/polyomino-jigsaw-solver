"""PuzzlePiece class for representing polyomino puzzle pieces."""

from __future__ import annotations

from src.logic.validator import is_contiguous


class PuzzlePiece:
    """Represents a single polyomino piece with its shape.

    Pieces are identified by their shape for dictionary storage.
    All transformations (rotations, reflections) are precomputed.

    Attributes:
        orientations: All unique precomputed transformations (rotations + reflections)
        canonical_shape: Smallest normalized orientation (used for equality/hash)
        area: Number of cells in the piece
        bounding_box: Tuple of (min_row, max_row, min_col, max_col)
    """

    def __init__(self, shape: set[tuple[int, int]]) -> None:
        """Initialize a puzzle piece.

        Args:
            shape: Set of (row, col) coordinates defining the piece shape

        Raises:
            ValueError: If shape is empty or not contiguous
        """
        if not shape:
            raise ValueError("Shape cannot be empty")
        if not is_contiguous(shape):
            raise ValueError("Shape must be contiguous (all cells connected)")

        # Compute all unique orientations (rotations + reflections)
        self._orientations = self._compute_all_orientations(shape)
        # Canonical shape = sorted smallest orientation (for equality/hash)
        # Sort by string representation for consistent ordering across equivalent pieces
        self._canonical_shape = min(self._orientations, key=lambda s: tuple(sorted(s)))
        # Precomputed attributes
        self._area = len(self._canonical_shape)
        self._bounding_box = self._compute_bounding_box(self._canonical_shape)

    def _compute_all_orientations(
        self, shape: set[tuple[int, int]]
    ) -> frozenset[frozenset[tuple[int, int]]]:
        """Compute and cache all unique orientations (8 max: 4 rotations × 2 mirrors).

        Returns:
            Frozenset of unique PuzzlePiece orientations (deduplicated)
        """
        orientations: set[frozenset[tuple[int, int]]] = set()

        # Generate 4 rotations × 2 flips
        current_shape = shape
        for _ in range(4):
            # Add original (not flipped) rotation
            normalized = self._normalize_shape(current_shape)
            orientations.add(frozenset(normalized))
            # Add flipped version (horizontal flip)
            flipped_shape = self._flip_shape(current_shape)
            orientations.add(frozenset(self._normalize_shape(flipped_shape)))
            # Rotate 90° for next iteration
            current_shape = self._rotate_shape(current_shape)

        return frozenset(orientations)

    def _normalize_shape(self, shape: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """Shift shape so min row/col = 0."""
        if not shape:
            return set()
        min_row = min(r for r, c in shape)
        min_col = min(c for r, c in shape)
        return {(r - min_row, c - min_col) for r, c in shape}

    def _rotate_shape(self, shape: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """Rotate shape 90 degrees clockwise around origin."""
        new_shape = {(col, -row) for row, col in shape}
        min_row = min(row for row, _ in new_shape)
        min_col = min(col for _, col in new_shape)
        return {(row - min_row, col - min_col) for row, col in new_shape}

    def _flip_shape(self, shape: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """Flip (mirror) shape horizontally."""
        new_shape = {(row, -col) for row, col in shape}
        min_row = min(row for row, _ in new_shape)
        min_col = min(col for _, col in new_shape)
        return {(row - min_row, col - min_col) for row, col in new_shape}

    def _compute_bounding_box(
        self, shape: frozenset[tuple[int, int]]
    ) -> tuple[int, int, int, int]:
        """Compute bounding box from canonical shape."""
        min_row = min(r for r, c in shape)
        max_row = max(r for r, c in shape)
        min_col = min(c for r, c in shape)
        max_col = max(c for r, c in shape)
        return (min_row, max_row, min_col, max_col)

    @property
    def orientations(self) -> frozenset[frozenset[tuple[int, int]]]:
        """All unique precomputed orientations (rotations + reflections)."""
        return self._orientations

    @property
    def canonical_shape(self) -> frozenset[tuple[int, int]]:
        """Smallest normalized orientation (used for equality/hash)."""
        return self._canonical_shape

    @property
    def area(self) -> int:
        """Number of cells in the piece."""
        return self._area

    @property
    def bounding_box(self) -> tuple[int, int, int, int]:
        """Bounding box as (min_row, max_row, min_col, max_col)."""
        return self._bounding_box

    @property
    def width(self) -> int:
        """Piece width (max_col - min_col + 1)."""
        _, _, min_col, max_col = self._bounding_box
        return max_col - min_col + 1

    @property
    def height(self) -> int:
        """Piece height (max_row - min_row + 1)."""
        min_row, max_row, _, _ = self._bounding_box
        return max_row - min_row + 1

    def __eq__(self, other: object) -> bool:
        """Check equality with another piece.

        Two pieces are equal if they have the same shape regardless of
        position, rotation, or flip.
        """
        if not isinstance(other, PuzzlePiece):
            return NotImplemented
        return self._canonical_shape == other._canonical_shape

    def __hash__(self) -> int:
        """Make piece hashable for use in sets and dicts.

        Uses canonical shape so rotated/flipped versions hash the same.
        """
        return hash(self._canonical_shape)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"PuzzlePiece(canonical_shape={self._canonical_shape})"
