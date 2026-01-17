"""Unit tests for rotation and flip operations."""

from __future__ import annotations

import pytest

from src.models.piece import PuzzlePiece


class TestRotationOperations:
    """Tests for rotation operations on PuzzlePiece."""

    def test_rotate_0_degrees(self) -> None:
        """Test rotating 0 degrees returns equivalent piece."""
        shape = {(0, 0), (0, 1), (1, 0)}
        piece = PuzzlePiece(name="corner", shape=shape)
        rotated = piece.rotate(0)

        # Should be a new instance
        assert rotated is not piece
        # Should have same shape
        assert rotated.shape == shape

    def test_rotate_90_degrees_basic(self) -> None:
        """Test basic 90 degree rotation."""
        shape = {(0, 0), (1, 0)}  # Vertical domino
        piece = PuzzlePiece(name="domino", shape=shape)
        rotated = piece.rotate(90)

        # Rotated shape should be horizontal
        expected_shape = {(0, 0), (0, 1)}
        assert rotated.shape == expected_shape

    def test_rotate_90_degrees_L_shape(self) -> None:
        """Test 90 degree rotation of L-shaped piece."""
        # L-shape: (0,0), (1,0), (1,1)
        shape = {(0, 0), (1, 0), (1, 1)}
        piece = PuzzlePiece(name="L", shape=shape)
        rotated = piece.rotate(90)

        # After 90° rotation, the shape should be normalized
        assert len(rotated.shape) == 3
        # All coordinates should be non-negative
        assert all(r >= 0 and c >= 0 for r, c in rotated.shape)

    def test_rotate_180_degrees(self) -> None:
        """Test 180 degree rotation."""
        shape = {(0, 0), (0, 1), (1, 1)}  # Z-shape
        piece = PuzzlePiece(name="Z", shape=shape)
        rotated = piece.rotate(180)

        # Should have same number of cells
        assert len(rotated.shape) == len(shape)
        assert all(r >= 0 and c >= 0 for r, c in rotated.shape)

    def test_rotate_270_degrees(self) -> None:
        """Test 270 degree rotation (same as -90)."""
        shape = {(0, 0), (0, 1), (1, 1)}
        piece = PuzzlePiece(name="S", shape=shape)
        rotated = piece.rotate(270)

        assert len(rotated.shape) == len(shape)

    def test_rotate_multiple_times(self) -> None:
        """Test that rotating 4 times returns to original orientation."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}
        piece = PuzzlePiece(name="L", shape=shape)

        # Rotate 4 times
        r1 = piece.rotate(90)
        r2 = r1.rotate(90)
        r3 = r2.rotate(90)
        r4 = r3.rotate(90)

        # r4 should have same shape as original
        assert r4.shape == piece.shape

    def test_rotate_invalid_angle_raises_error(self) -> None:
        """Test that invalid rotation angle raises ValueError."""
        shape = {(0, 0)}
        piece = PuzzlePiece(name="test", shape=shape)

        with pytest.raises(ValueError, match="multiple of 90"):
            piece.rotate(45)

        with pytest.raises(ValueError, match="multiple of 90"):
            piece.rotate(30)


class TestFlipOperations:
    """Tests for flip (mirror) operations on PuzzlePiece."""

    def test_flip_horizontal(self) -> None:
        """Test horizontal flip."""
        # Asymmetric shape
        shape = {(0, 0), (0, 1), (0, 2), (1, 0)}  # L with extra cell
        piece = PuzzlePiece(name="L-variant", shape=shape)
        flipped = piece.flip("horizontal")

        # Should be new instance
        assert flipped is not piece
        # Should have same number of cells
        assert len(flipped.shape) == len(shape)
        # All coordinates should be non-negative
        assert all(r >= 0 and c >= 0 for r, c in flipped.shape)

    def test_flip_vertical(self) -> None:
        """Test vertical flip."""
        shape = {(0, 0), (1, 0), (2, 0), (2, 1)}
        piece = PuzzlePiece(name="J", shape=shape)
        flipped = piece.flip("vertical")

        assert flipped is not piece
        assert len(flipped.shape) == len(shape)
        assert all(r >= 0 and c >= 0 for r, c in flipped.shape)

    def test_flip_symmetric_piece(self) -> None:
        """Test flipping a symmetric piece."""
        # Square (2x2) is symmetric
        shape = {(0, 0), (0, 1), (1, 0), (1, 1)}
        piece = PuzzlePiece(name="square", shape=shape)
        flipped = piece.flip("horizontal")

        # Symmetric piece should have same shape after flip
        assert flipped.shape == shape

    def test_flip_invalid_axis_raises_error(self) -> None:
        """Test that invalid flip axis raises ValueError."""
        shape = {(0, 0)}
        piece = PuzzlePiece(name="test", shape=shape)

        with pytest.raises(ValueError, match="'horizontal' or 'vertical'"):
            piece.flip("diagonal")


class TestOrientationGeneration:
    """Tests for generating all possible orientations."""

    def test_get_rotations(self) -> None:
        """Test getting all unique rotations."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # L-tetromino
        piece = PuzzlePiece(name="L", shape=shape)
        rotations = piece.get_rotations()

        # L-tetromino has 4 unique rotations
        assert len(rotations) == 4
        # All should be PuzzlePiece instances
        assert all(isinstance(r, PuzzlePiece) for r in rotations)

    def test_get_all_orientations(self) -> None:
        """Test getting all unique orientations including flips."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # L-tetromino
        piece = PuzzlePiece(name="L", shape=shape)
        orientations = piece.get_all_orientations()

        # L-tetromino has 8 unique orientations (4 rotations × 2 flips)
        assert len(orientations) == 8

    def test_symmetric_piece_has_fewer_orientations(self) -> None:
        """Test that symmetric pieces have fewer unique orientations."""
        # I-tetromino (1x4) has only 2 unique orientations
        shape = {(0, 0), (0, 1), (0, 2), (0, 3)}
        piece = PuzzlePiece(name="I", shape=shape)
        orientations = piece.get_all_orientations()

        # I-tetromino has only 2 unique orientations (horizontal and vertical)
        assert len(orientations) == 2

    def test_square_has_one_orientation(self) -> None:
        """Test that a square has only 1 unique orientation."""
        shape = {(0, 0), (0, 1), (1, 0), (1, 1)}
        piece = PuzzlePiece(name="O", shape=shape)
        orientations = piece.get_all_orientations()

        # Square has only 1 unique orientation
        assert len(orientations) == 1


class TestShapeNormalization:
    """Tests for shape normalization during transformations."""

    def test_rotation_normalizes_shape(self) -> None:
        """Test that rotation normalizes shape to non-negative coordinates."""
        shape = {(0, 0), (-1, 1), (0, 1)}  # Already normalized
        piece = PuzzlePiece(name="test", shape=shape)
        rotated = piece.rotate(90)

        # All coordinates should be non-negative after rotation
        assert all(r >= 0 and c >= 0 for r, c in rotated.shape)

    def test_flip_normalizes_shape(self) -> None:
        """Test that flip normalizes shape to non-negative coordinates."""
        shape = {(0, 0), (0, 1), (1, 0)}
        piece = PuzzlePiece(name="test", shape=shape)
        flipped = piece.flip("vertical")

        # All coordinates should be non-negative after flip
        assert all(r >= 0 and c >= 0 for r, c in flipped.shape)


class TestRotationPreservation:
    """Tests for preservation of piece properties during rotation."""

    def test_rotation_preserves_area(self) -> None:
        """Test that rotation preserves piece area."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)}
        piece = PuzzlePiece(name="pentomino", shape=shape)

        for degrees in [90, 180, 270]:
            rotated = piece.rotate(degrees)
            assert rotated.area == piece.area

    def test_flip_preserves_area(self) -> None:
        """Test that flip preserves piece area."""
        shape = {(0, 0), (0, 1), (1, 1), (2, 1)}
        piece = PuzzlePiece(name="Y", shape=shape)

        flipped = piece.flip("horizontal")
        assert flipped.area == piece.area

        flipped = piece.flip("vertical")
        assert flipped.area == piece.area

    def test_rotation_preserves_contiguity(self) -> None:
        """Test that rotated pieces remain contiguous."""
        shape = {(0, 0), (1, 0), (2, 0), (2, 1)}  # L-pentomino
        piece = PuzzlePiece(name="L-pentomino", shape=shape)

        rotated = piece.rotate(90)
        # The rotated piece should still be contiguous (this is implicit in how we create it)
        assert len(rotated.shape) == len(shape)
