"""Unit tests for PuzzlePiece class."""

from __future__ import annotations

import pytest

from src.models.piece import PuzzlePiece


class TestPuzzlePieceCreation:
    """Test PuzzlePiece initialization and basic properties."""

    def test_create_piece_with_valid_shape(self) -> None:
        """Test creating a piece with a valid contiguous shape."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # L-tetromino
        piece = PuzzlePiece(name="L-tetromino", shape=shape)

        assert piece.name == "L-tetromino"
        assert piece.shape == shape

    def test_create_piece_with_empty_shape_raises_error(self) -> None:
        """Test that creating a piece with empty shape raises ValueError."""
        with pytest.raises(ValueError, match="Shape cannot be empty"):
            PuzzlePiece(name="Empty", shape=set())

    def test_create_piece_with_non_contiguous_shape_raises_error(self) -> None:
        """Test that creating a piece with non-contiguous shape raises ValueError."""
        # Two separate cells (not connected)
        shape = {(0, 0), (0, 2)}
        with pytest.raises(ValueError, match="Shape must be contiguous"):
            PuzzlePiece(name="Disconnected", shape=shape)

    def test_create_piece_with_single_cell(self) -> None:
        """Test creating a piece with a single cell (monomino)."""
        shape = {(0, 0)}
        piece = PuzzlePiece(name="Monomino", shape=shape)

        assert piece.shape == shape
        assert len(piece.shape) == 1


class TestPuzzlePieceProperties:
    """Test PuzzlePiece computed properties."""

    def test_area_property(self) -> None:
        """Test that area property returns correct cell count."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # 4 cells
        piece = PuzzlePiece(name="L-tetromino", shape=shape)

        assert piece.area == 4

    def test_bounding_box(self) -> None:
        """Test bounding box calculation."""
        shape = {(1, 1), (1, 2), (2, 1)}  # L shape offset from origin
        piece = PuzzlePiece(name="L-small", shape=shape)

        min_row, max_row, min_col, max_col = piece.get_bounding_box()
        assert min_row == 1
        assert max_row == 2
        assert min_col == 1
        assert max_col == 2

    def test_width_property(self) -> None:
        """Test width property calculation."""
        shape = {(0, 0), (0, 1), (0, 2)}  # 3 cells wide
        piece = PuzzlePiece(name="I-tri", shape=shape)

        assert piece.width == 3

    def test_height_property(self) -> None:
        """Test height property calculation."""
        shape = {(0, 0), (1, 0), (2, 0)}  # 3 cells tall
        piece = PuzzlePiece(name="I-tri", shape=shape)

        assert piece.height == 3


class TestPuzzlePieceRotation:
    """Test PuzzlePiece rotation operations."""

    def test_rotate_90_degrees(self) -> None:
        """Test 90-degree rotation."""
        shape = {(0, 0), (1, 0), (1, 1)}  # Small L
        piece = PuzzlePiece(name="L-small", shape=shape)
        rotated = piece.rotate(90)

        # Original shape should be unchanged (immutability)
        assert piece.shape == shape

        # Rotated shape should have different coordinates
        assert rotated.shape != shape

    def test_rotate_180_degrees(self) -> None:
        """Test 180-degree rotation."""
        shape = {(0, 0), (0, 1), (1, 1)}  # Small L
        piece = PuzzlePiece(name="L-small", shape=shape)
        rotated = piece.rotate(180)

        assert piece.shape == shape
        assert rotated.shape != shape

    def test_rotate_270_degrees(self) -> None:
        """Test 270-degree rotation."""
        shape = {(0, 0), (1, 0), (1, 1)}  # Small L
        piece = PuzzlePiece(name="L-small", shape=shape)
        rotated = piece.rotate(270)

        assert piece.shape == shape
        assert rotated.shape != shape

    def test_rotate_0_degrees_returns_copy(self) -> None:
        """Test that 0-degree rotation returns a new copy."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece(name="L-small", shape=shape)
        rotated = piece.rotate(0)

        # Should be equal in value but different object (immutability)
        assert rotated.shape == shape
        assert rotated is not piece

    def test_rotate_invalid_angle_raises_error(self) -> None:
        """Test that invalid rotation angle raises ValueError."""
        shape = {(0, 0), (1, 0)}
        piece = PuzzlePiece(name="Domino", shape=shape)

        with pytest.raises(ValueError, match="Rotation must be a multiple of 90"):
            piece.rotate(45)


class TestPuzzlePieceFlip:
    """Test PuzzlePiece flip (mirror) operations."""

    def test_flip_horizontal(self) -> None:
        """Test horizontal flip."""
        shape = {(0, 0), (0, 1), (1, 1)}  # L shape
        piece = PuzzlePiece(name="L-shape", shape=shape)
        flipped = piece.flip("horizontal")

        assert piece.shape == shape  # Original unchanged
        assert flipped.shape != shape  # Flipped is different

    def test_flip_vertical(self) -> None:
        """Test vertical flip."""
        shape = {(0, 0), (0, 1), (1, 1)}  # L shape
        piece = PuzzlePiece(name="L-shape", shape=shape)
        flipped = piece.flip("vertical")

        assert piece.shape == shape
        assert flipped.shape != shape

    def test_flip_invalid_axis_raises_error(self) -> None:
        """Test that invalid flip axis raises ValueError."""
        shape = {(0, 0), (1, 0)}
        piece = PuzzlePiece(name="Domino", shape=shape)

        with pytest.raises(ValueError, match="Axis must be 'horizontal' or 'vertical'"):
            piece.flip("diagonal")


class TestPuzzlePieceOrientations:
    """Test PuzzlePiece orientation generation."""

    def test_get_rotations_returns_list(self) -> None:
        """Test that get_rotations returns a list."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece(name="L", shape=shape)
        rotations = piece.get_rotations()

        assert isinstance(rotations, list)
        assert len(rotations) > 0

    def test_get_all_orientations_includes_flips(self) -> None:
        """Test that get_all_orientations includes flipped versions."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece(name="L", shape=shape)
        orientations = piece.get_all_orientations()

        assert isinstance(orientations, list)
        # Should have more orientations than just rotations
        assert len(orientations) >= len(piece.get_rotations())

    def test_precomputed_orientations_exist(self) -> None:
        """Test that precomputed orientations are available."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece(name="L", shape=shape)

        orientations = piece.get_precomputed_orientations()
        assert isinstance(orientations, list)
        # Should have 1-8 orientations depending on symmetry

    def test_symmetric_piece_has_fewer_orientations(self) -> None:
        """Test that symmetric pieces have fewer unique orientations."""
        # Square (2x2) - very symmetric
        square_shape = {(0, 0), (0, 1), (1, 0), (1, 1)}
        square = PuzzlePiece(name="Square", shape=square_shape)

        # Line - symmetric
        line_shape = {(0, 0), (0, 1), (0, 2), (0, 3)}
        line = PuzzlePiece(name="Line", shape=line_shape)

        # L shape - asymmetric
        l_shape = {(0, 0), (1, 0), (1, 1), (1, 2)}
        l_piece = PuzzlePiece(name="L", shape=l_shape)

        # Symmetric pieces should have fewer orientations
        assert len(square.get_precomputed_orientations()) <= len(
            l_piece.get_precomputed_orientations()
        )


class TestPuzzlePieceNormalization:
    """Test PuzzlePiece shape normalization."""

    def test_normalized_shape_at_origin(self) -> None:
        """Test that shape is normalized to origin (0,0)."""
        # Shape with coordinates not starting at 0
        shape = {(5, 5), (6, 5), (6, 6)}
        piece = PuzzlePiece(name="Offset-L", shape=shape)
        normalized = piece.get_normalized_shape()

        # Normalized shape should have min row and col at 0
        min_row = min(r for r, c in normalized)
        min_col = min(c for r, c in normalized)
        assert min_row == 0
        assert min_col == 0

    def test_normalized_shape_preserves_relative_positions(self) -> None:
        """Test that normalization preserves relative cell positions."""
        shape = {(5, 5), (6, 5), (6, 6)}
        piece = PuzzlePiece(name="Offset-L", shape=shape)
        normalized = piece.get_normalized_shape()

        # Relative positions should be preserved
        assert (0, 0) in normalized
        assert (1, 0) in normalized
        assert (1, 1) in normalized


class TestPuzzlePieceWithId:
    """Test PuzzlePiece.with_id factory method."""

    def test_with_id_creates_piece_with_id_name(self) -> None:
        """Test that with_id creates piece with the id as name."""
        shape = {(0, 0), (1, 0)}
        piece = PuzzlePiece.with_id(shape=shape, id="piece-123")

        assert piece.name == "piece-123"
        assert piece.shape == shape

    def test_with_id_returns_valid_piece(self) -> None:
        """Test that with_id returns a fully functional piece."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece.with_id(shape=shape, id="test-piece")

        # Should be able to rotate, flip, etc.
        rotated = piece.rotate(90)
        assert rotated.shape != piece.shape
        assert len(rotated.shape) == len(piece.shape)
