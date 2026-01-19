"""Unit tests for PuzzlePiece class."""

from __future__ import annotations

import pytest

from src.models.piece import PuzzlePiece


class TestPuzzlePieceCreation:
    """Test PuzzlePiece initialization and basic properties."""

    def test_create_piece_with_valid_shape(self) -> None:
        """Test creating a piece with a valid contiguous shape."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # L-tetromino
        piece = PuzzlePiece(shape=shape)

        # canonical_shape is the smallest orientation (lexicographically), not necessarily the input
        assert isinstance(piece.canonical_shape, frozenset)
        assert len(piece.canonical_shape) == 4

    def test_create_piece_with_empty_shape_raises_error(self) -> None:
        """Test that creating a piece with empty shape raises ValueError."""
        with pytest.raises(ValueError, match="Shape cannot be empty"):
            PuzzlePiece(shape=set())

    def test_create_piece_with_non_contiguous_shape_raises_error(self) -> None:
        """Test that creating a piece with non-contiguous shape raises ValueError."""
        # Two separate cells (not connected)
        shape = {(0, 0), (0, 2)}
        with pytest.raises(ValueError, match="Shape must be contiguous"):
            PuzzlePiece(shape=shape)

    def test_create_piece_with_single_cell(self) -> None:
        """Test creating a piece with a single cell (monomino)."""
        shape = {(0, 0)}
        piece = PuzzlePiece(shape=shape)

        assert piece.canonical_shape == frozenset(shape)
        assert piece.area == 1


class TestPuzzlePieceProperties:
    """Test PuzzlePiece computed properties."""

    def test_area_property(self) -> None:
        """Test that area property returns correct cell count."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # 4 cells
        piece = PuzzlePiece(shape=shape)

        assert piece.area == 4

    def test_bounding_box(self) -> None:
        """Test bounding box calculation."""
        shape = {(1, 1), (1, 2), (2, 1)}  # L shape offset from origin
        piece = PuzzlePiece(shape=shape)

        min_row, max_row, min_col, max_col = piece.bounding_box
        # Shape is normalized to origin, so min_row=0, min_col=0
        assert min_row == 0
        assert max_row == 1
        assert min_col == 0
        assert max_col == 1

    def test_width_property(self) -> None:
        """Test width property calculation."""
        shape = {(0, 0), (0, 1), (0, 2)}  # 3 cells wide
        piece = PuzzlePiece(shape=shape)

        assert piece.width == 3

    def test_height_property(self) -> None:
        """Test height property calculation."""
        shape = {(0, 0), (1, 0), (2, 0)}  # 3 cells tall
        piece = PuzzlePiece(shape=shape)

        # Height is based on canonical_shape which is the "smallest" orientation
        # A line's canonical form is horizontal, so height is 1
        assert piece.height == 1


class TestPuzzlePieceOrientations:
    """Test PuzzlePiece orientation generation."""

    def test_orientations_property_returns_frozenset(self) -> None:
        """Test that orientations property returns a frozenset."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece(shape=shape)

        assert isinstance(piece.orientations, frozenset)

    def test_orientations_contains_all_transformations(self) -> None:
        """Test that orientations contains rotations and reflections."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece(shape=shape)
        orientations = piece.orientations

        # Should have multiple orientations
        assert len(orientations) > 0

    def test_symmetric_piece_has_fewer_orientations(self) -> None:
        """Test that symmetric pieces have fewer unique orientations."""
        # Square (2x2) - very symmetric
        square_shape = {(0, 0), (0, 1), (1, 0), (1, 1)}
        square = PuzzlePiece(shape=square_shape)

        # Line - symmetric
        line_shape = {(0, 0), (0, 1), (0, 2), (0, 3)}
        line = PuzzlePiece(shape=line_shape)

        # L shape - asymmetric
        l_shape = {(0, 0), (1, 0), (1, 1), (1, 2)}
        l_piece = PuzzlePiece(shape=l_shape)

        # Symmetric pieces should have fewer orientations
        assert len(square.orientations) <= len(l_piece.orientations)
        assert len(line.orientations) <= len(l_piece.orientations)

    def test_canonical_shape_is_in_orientations(self) -> None:
        """Test that canonical shape is one of the orientations."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece(shape=shape)

        assert piece.canonical_shape in piece.orientations


class TestPuzzlePieceEquality:
    """Test PuzzlePiece equality and hashing."""

    def test_equal_pieces_with_same_shape(self) -> None:
        """Test that pieces with same shape are equal."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece1 = PuzzlePiece(shape=shape)
        piece2 = PuzzlePiece(shape=shape)

        assert piece1 == piece2
        assert hash(piece1) == hash(piece2)

    def test_equal_pieces_with_different_positions(self) -> None:
        """Test that pieces are equal regardless of position."""
        shape1 = {(0, 0), (1, 0), (1, 1)}
        shape2 = {(5, 5), (6, 5), (6, 6)}  # Same shape, different position

        piece1 = PuzzlePiece(shape=shape1)
        piece2 = PuzzlePiece(shape=shape2)

        assert piece1 == piece2
        assert hash(piece1) == hash(piece2)

    def test_equal_pieces_with_rotations(self) -> None:
        """Test that rotated pieces are equal."""
        shape1 = {(0, 0), (1, 0), (1, 1)}  # Original
        shape2 = {(0, 0), (0, 1), (1, 0)}  # Same shape, different rotation

        piece1 = PuzzlePiece(shape=shape1)
        piece2 = PuzzlePiece(shape=shape2)

        assert piece1 == piece2
        assert hash(piece1) == hash(piece2)

    def test_unequal_pieces(self) -> None:
        """Test that different shapes are not equal."""
        shape1 = {(0, 0), (1, 0), (1, 1)}  # L shape
        shape2 = {(0, 0), (0, 1), (0, 2), (1, 1)}  # T shape

        piece1 = PuzzlePiece(shape=shape1)
        piece2 = PuzzlePiece(shape=shape2)

        assert piece1 != piece2

    def test_equality_with_non_puzzle_piece(self) -> None:
        """Test equality with non-PuzzlePiece returns NotImplemented."""
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece(shape=shape)

        assert (piece == "not a piece") is False
        assert (piece == 42) is False
        assert (piece == None) is False

    def test_can_be_used_in_set(self) -> None:
        """Test that pieces can be used in sets."""
        shape1 = {(0, 0), (1, 0), (1, 1)}  # L-tromino
        shape2 = {(0, 0), (0, 1), (1, 0)}  # Same L-tromino, different orientation
        shape3 = {(0, 0), (1, 0), (1, 1)}  # Same as shape1

        piece1 = PuzzlePiece(shape=shape1)
        piece2 = PuzzlePiece(shape=shape2)
        piece3 = PuzzlePiece(shape=shape3)

        piece_set = {piece1, piece2, piece3}

        # All three pieces are the same L-tromino (just different orientations)
        assert len(piece_set) == 1
        assert piece1 in piece_set
        assert piece2 in piece_set
        assert piece3 in piece_set

    def test_can_be_used_as_dict_key(self) -> None:
        """Test that pieces can be used as dictionary keys."""
        shape1 = {(0, 0), (1, 0), (1, 1)}  # L-tromino
        shape2 = {(0, 0), (0, 1), (1, 0)}  # Same L-tromino, different orientation
        shape3 = {(0, 0), (1, 0), (1, 1)}  # Same as shape1

        piece1 = PuzzlePiece(shape=shape1)
        piece2 = PuzzlePiece(shape=shape2)
        piece3 = PuzzlePiece(shape=shape3)

        piece_dict: dict[PuzzlePiece, str] = {}

        piece_dict[piece1] = "first"
        piece_dict[piece2] = "second"
        piece_dict[piece3] = "third"  # Should overwrite piece1 and piece2

        # All three pieces are the same L-tromino
        assert len(piece_dict) == 1
        assert piece_dict[piece1] == "third"
        assert piece_dict[piece2] == "third"
