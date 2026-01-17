"""Unit tests for PuzzlePiece class."""

from __future__ import annotations

import pytest

from src.models.piece import PuzzlePiece


class TestPuzzlePieceCreation:
    """Tests for PuzzlePiece creation and basic properties."""

    def test_create_piece_with_name_and_shape(self) -> None:
        """Test creating a piece with name and shape."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}
        piece = PuzzlePiece(name="L-tetromino", shape=shape)

        assert piece.name == "L-tetromino"
        assert piece.shape == shape
        assert piece.area == 4

    def test_create_piece_with_single_cell(self) -> None:
        """Test creating a piece with a single cell."""
        shape = {(0, 0)}
        piece = PuzzlePiece(name="monomino", shape=shape)

        assert piece.name == "monomino"
        assert piece.shape == shape
        assert piece.area == 1

    def test_create_piece_empty_shape_raises_error(self) -> None:
        """Test that creating a piece with empty shape raises ValueError."""
        with pytest.raises(ValueError, match="Shape cannot be empty"):
            PuzzlePiece(name="empty", shape=set())

    def test_create_piece_non_contiguous_shape_raises_error(self) -> None:
        """Test that creating a piece with non-contiguous shape raises ValueError."""
        # Two separate cells that are not connected
        shape = {(0, 0), (0, 2)}
        with pytest.raises(ValueError, match="Shape must be contiguous"):
            PuzzlePiece(name="disconnected", shape=shape)


class TestPuzzlePieceProperties:
    """Tests for PuzzlePiece property accessors."""

    def test_piece_name_property(self) -> None:
        """Test that name property returns correct value."""
        shape = {(0, 0)}
        piece = PuzzlePiece(name="test-piece", shape=shape)
        assert piece.name == "test-piece"

    def test_piece_shape_property_returns_copy(self) -> None:
        """Test that shape property returns a copy, not the original."""
        original_shape = {(0, 0), (1, 0)}
        piece = PuzzlePiece(name="test", shape=original_shape)

        # Get shape and modify it
        returned_shape = piece.shape
        returned_shape.add((2, 2))

        # Original piece shape should be unchanged
        assert (2, 2) not in piece.shape

    def test_piece_area_property(self) -> None:
        """Test that area property returns correct count."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)}
        piece = PuzzlePiece(name="pentomino", shape=shape)
        assert piece.area == 5

    def test_piece_width_property(self) -> None:
        """Test that width property returns correct value."""
        shape = {(0, 0), (0, 1), (0, 2)}
        piece = PuzzlePiece(name="I-piece", shape=shape)
        assert piece.width == 3

    def test_piece_height_property(self) -> None:
        """Test that height property returns correct value."""
        shape = {(0, 0), (1, 0), (2, 0)}
        piece = PuzzlePiece(name="I-piece", shape=shape)
        assert piece.height == 3


class TestPuzzlePieceRotation:
    """Tests for PuzzlePiece rotation operations."""

    def test_rotate_90_degrees(self) -> None:
        """Test rotating a piece 90 degrees."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # L-shape
        piece = PuzzlePiece(name="L", shape=shape)
        rotated = piece.rotate(90)

        # Verify it's a new piece
        assert rotated is not piece
        # Verify rotation preserves area
        assert rotated.area == piece.area
        # Verify name contains rotation indicator
        assert "rot90" in rotated.name

    def test_rotate_180_degrees(self) -> None:
        """Test rotating a piece 180 degrees."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # L-shape
        piece = PuzzlePiece(name="L", shape=shape)
        rotated = piece.rotate(180)

        assert rotated is not piece
        assert rotated.area == piece.area
        assert "rot180" in rotated.name

    def test_rotate_270_degrees(self) -> None:
        """Test rotating a piece 270 degrees."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # L-shape
        piece = PuzzlePiece(name="L", shape=shape)
        rotated = piece.rotate(270)

        assert rotated is not piece
        assert rotated.area == piece.area
        assert "rot270" in rotated.name

    def test_rotate_0_degrees_returns_copy(self) -> None:
        """Test that rotating 0 degrees returns a copy."""
        shape = {(0, 0), (1, 0)}
        piece = PuzzlePiece(name="domino", shape=shape)
        rotated = piece.rotate(0)

        # Should be a different object (copy)
        assert rotated is not piece
        # But with same shape
        assert rotated.shape == piece.shape

    def test_rotate_invalid_angle_raises_error(self) -> None:
        """Test that rotating by invalid angle raises ValueError."""
        shape = {(0, 0)}
        piece = PuzzlePiece(name="test", shape=shape)

        with pytest.raises(ValueError, match="Rotation must be a multiple of 90"):
            piece.rotate(45)


class TestPuzzlePieceFlip:
    """Tests for PuzzlePiece flip operations."""

    def test_flip_horizontal(self) -> None:
        """Test flipping a piece horizontally."""
        shape = {(0, 0), (0, 1), (0, 2), (1, 1)}  # T-shape
        piece = PuzzlePiece(name="T", shape=shape)
        flipped = piece.flip("horizontal")

        assert flipped is not piece
        assert flipped.area == piece.area
        assert "fliph" in flipped.name

    def test_flip_vertical(self) -> None:
        """Test flipping a piece vertically."""
        shape = {(0, 0), (0, 1), (0, 2), (1, 1)}  # T-shape
        piece = PuzzlePiece(name="T", shape=shape)
        flipped = piece.flip("vertical")

        assert flipped is not piece
        assert flipped.area == piece.area
        assert "flipv" in flipped.name

    def test_flip_invalid_axis_raises_error(self) -> None:
        """Test that flipping with invalid axis raises ValueError."""
        shape = {(0, 0)}
        piece = PuzzlePiece(name="test", shape=shape)

        with pytest.raises(ValueError, match="Axis must be 'horizontal' or 'vertical'"):
            piece.flip("diagonal")


class TestPuzzlePieceNormalization:
    """Tests for PuzzlePiece shape normalization."""

    def test_normalize_shape(self) -> None:
        """Test getting normalized shape."""
        # Shape with negative coordinates
        shape = {(-1, -1), (-1, 0), (0, -1)}
        piece = PuzzlePiece(name="corner", shape=shape)

        normalized = piece.get_normalized_shape()

        # All coordinates should be non-negative
        assert all(r >= 0 and c >= 0 for r, c in normalized)
        # Minimum should be (0, 0)
        assert (0, 0) in normalized

    def test_bounding_box(self) -> None:
        """Test getting bounding box."""
        shape = {(0, 0), (0, 2), (2, 0), (2, 2)}  # Square corners
        piece = PuzzlePiece(name="square", shape=shape)

        min_row, max_row, min_col, max_col = piece.get_bounding_box()

        assert min_row == 0
        assert max_row == 2
        assert min_col == 0
        assert max_col == 2


class TestPuzzlePieceOrientations:
    """Tests for PuzzlePiece orientation generation."""

    def test_get_rotations(self) -> None:
        """Test getting all unique rotations."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # L-shape
        piece = PuzzlePiece(name="L", shape=shape)
        rotations = piece.get_rotations()

        # Should have 4 rotations for L-shape
        assert len(rotations) == 4
        # All should be PuzzlePiece instances
        assert all(isinstance(r, PuzzlePiece) for r in rotations)

    def test_get_all_orientations(self) -> None:
        """Test getting all unique orientations (rotations + flips)."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # L-shape
        piece = PuzzlePiece(name="L", shape=shape)
        orientations = piece.get_all_orientations()

        # Should have 8 orientations (4 rotations × 2 flips) for L-shape
        assert len(orientations) == 8

    def test_precomputed_orientations(self) -> None:
        """Test precomputed orientations are available."""
        shape = {(0, 0), (1, 0)}
        piece = PuzzlePiece(name="domino", shape=shape)
        orientations = piece.get_precomputed_orientations()

        # Should have precomputed orientations
        assert len(orientations) > 0
        assert all(isinstance(o, PuzzlePiece) for o in orientations)


class TestPuzzlePieceEquality:
    """Tests for PuzzlePiece equality and hashing."""

    def test_equal_pieces(self) -> None:
        """Test that pieces with same name and shape are equal."""
        shape = {(0, 0), (1, 0)}
        piece1 = PuzzlePiece(name="domino", shape=shape)
        piece2 = PuzzlePiece(name="domino", shape=shape)

        assert piece1 == piece2

    def test_unequal_pieces_different_name(self) -> None:
        """Test that pieces with different names are not equal."""
        shape = {(0, 0), (1, 0)}
        piece1 = PuzzlePiece(name="domino1", shape=shape)
        piece2 = PuzzlePiece(name="domino2", shape=shape)

        assert piece1 != piece2

    def test_unequal_pieces_different_shape(self) -> None:
        """Test that pieces with different shapes are not equal."""
        shape1 = {(0, 0), (1, 0)}
        shape2 = {(0, 0), (0, 1)}
        piece1 = PuzzlePiece(name="piece", shape=shape1)
        piece2 = PuzzlePiece(name="piece", shape=shape2)

        assert piece1 != piece2

    def test_piece_hashable(self) -> None:
        """Test that pieces can be used in sets and as dict keys."""
        shape = {(0, 0), (1, 0)}
        piece1 = PuzzlePiece(name="domino", shape=shape)
        piece2 = PuzzlePiece(name="domino", shape=shape)

        # Use in a set
        piece_set = {piece1, piece2}
        assert len(piece_set) == 1

        # Use as a dict key
        piece_dict = {piece1: "value"}
        assert piece_dict[piece2] == "value"

    def test_repr(self) -> None:
        """Test string representation."""
        shape = {(0, 0)}
        piece = PuzzlePiece(name="monomino", shape=shape)

        repr_str = repr(piece)
        assert "monomino" in repr_str
        assert "PuzzlePiece" in repr_str


class TestPuzzlePieceFactory:
    """Tests for PuzzlePiece factory methods."""

    def test_with_id_factory(self) -> None:
        """Test with_id factory method creates piece with specified ID."""
        shape = {(0, 0)}
        piece = PuzzlePiece.with_id(shape=shape, id="custom-id")

        assert piece.name == "custom-id"
        assert piece.shape == shape


class TestPuzzlePieceCopy:
    """Tests for PuzzlePiece copy functionality."""

    def test_equality_with_rotated_copy(self) -> None:
        """Test that rotated piece is different but has same area."""
        shape = {(0, 0), (1, 0)}
        original = PuzzlePiece(name="domino", shape=shape)
        rotated = original.rotate(90)

        # Different pieces
        assert original != rotated
        # Same area
        assert original.area == rotated.area
        # Both are dominoes
        assert original.area == 2
        assert rotated.area == 2
