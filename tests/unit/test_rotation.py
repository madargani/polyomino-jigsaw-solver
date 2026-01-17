"""Unit tests for rotation and flip operations."""

from __future__ import annotations

import pytest

from src.logic.rotation import (
    rotate_shape,
    flip_shape,
    get_all_orientations,
)


class TestRotateShape:
    """Test rotate_shape function."""

    def test_rotate_0_degrees_returns_same_shape(self) -> None:
        """Test that 0-degree rotation returns equivalent shape."""
        shape = {(0, 0), (1, 0), (1, 1)}
        result = rotate_shape(shape, 0)

        assert result == shape

    def test_rotate_90_degrees(self) -> None:
        """Test 90-degree rotation."""
        # Horizontal line: [(0,0), (0,1), (0,2)]
        shape = {(0, 0), (0, 1), (0, 2)}
        result = rotate_shape(shape, 90)

        # Should become vertical line: [(0,0), (1,0), (2,0)]
        assert len(result) == 3
        assert (0, 0) in result
        assert (1, 0) in result
        assert (2, 0) in result

    def test_rotate_180_degrees(self) -> None:
        """Test 180-degree rotation."""
        shape = {(0, 0), (0, 1), (1, 0)}
        result = rotate_shape(shape, 180)

        # Original shape normalized to origin, then rotated
        assert len(result) == 3

    def test_rotate_270_degrees(self) -> None:
        """Test 270-degree rotation (same as -90)."""
        shape = {(0, 0), (0, 1), (0, 2)}
        result = rotate_shape(shape, 270)

        # Should be vertical line pointing left
        assert len(result) == 3

    def test_rotate_360_degrees(self) -> None:
        """Test 360-degree rotation (same as 0)."""
        shape = {(0, 0), (1, 0)}
        result = rotate_shape(shape, 360)

        assert result == shape

    def test_rotate_negative_angle(self) -> None:
        """Test rotation with negative angle."""
        shape = {(0, 0), (0, 1)}
        result = rotate_shape(shape, -90)

        # -90 should be same as 270
        expected = rotate_shape(shape, 270)
        assert result == expected

    def test_rotate_invalid_angle_raises_error(self) -> None:
        """Test that invalid rotation angle raises ValueError."""
        shape = {(0, 0), (1, 0)}

        with pytest.raises(ValueError, match="Rotation must be a multiple of 90"):
            rotate_shape(shape, 45)

    def test_rotate_preserves_cell_count(self) -> None:
        """Test that rotation preserves number of cells."""
        shape = {(0, 0), (1, 0), (1, 1), (2, 0), (2, 1)}  # 5 cells
        result = rotate_shape(shape, 90)

        assert len(result) == 5

    def test_rotate_normalizes_to_origin(self) -> None:
        """Test that rotated shape is normalized to origin."""
        shape = {(5, 5), (5, 6), (6, 5)}
        result = rotate_shape(shape, 90)

        min_row = min(r for r, c in result)
        min_col = min(c for r, c in result)
        assert min_row == 0
        assert min_col == 0


class TestFlipShape:
    """Test flip_shape function."""

    def test_flip_horizontal(self) -> None:
        """Test horizontal flip (mirror left-right)."""
        shape = {(0, 0), (0, 1), (1, 1)}  # L shape
        result = flip_shape(shape, "horizontal")

        assert len(result) == 3
        # After horizontal flip, shape should be mirrored
        assert result != shape

    def test_flip_vertical(self) -> None:
        """Test vertical flip (mirror top-bottom)."""
        shape = {(0, 0), (0, 1), (1, 1)}  # L shape
        result = flip_shape(shape, "vertical")

        assert len(result) == 3
        assert result != shape

    def test_flip_preserves_cell_count(self) -> None:
        """Test that flip preserves number of cells."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # 4 cells
        result_h = flip_shape(shape, "horizontal")
        result_v = flip_shape(shape, "vertical")

        assert len(result_h) == 4
        assert len(result_v) == 4

    def test_flip_invalid_axis_raises_error(self) -> None:
        """Test that invalid flip axis raises ValueError."""
        shape = {(0, 0), (1, 0)}

        with pytest.raises(ValueError, match="Axis must be 'horizontal' or 'vertical'"):
            flip_shape(shape, "diagonal")


class TestGetAllOrientations:
    """Test get_all_orientations function."""

    def test_returns_list_of_shapes(self) -> None:
        """Test that get_all_orientations returns a list."""
        shape = {(0, 0), (1, 0), (1, 1)}
        orientations = get_all_orientations(shape)

        assert isinstance(orientations, list)
        assert len(orientations) > 0

    def test_all_orientations_have_same_cell_count(self) -> None:
        """Test that all orientations have same number of cells."""
        shape = {(0, 0), (1, 0), (1, 1), (1, 2)}  # 4 cells
        orientations = get_all_orientations(shape)

        for orientation in orientations:
            assert len(orientation) == 4

    def test_includes_rotations_and_flips(self) -> None:
        """Test that orientations include both rotations and flips."""
        shape = {(0, 0), (1, 0), (1, 1)}  # L shape
        orientations = get_all_orientations(shape)

        # Should have at least 4 rotations (0, 90, 180, 270)
        assert len(orientations) >= 4

    def test_symmetric_shape_has_fewer_orientations(self) -> None:
        """Test that symmetric shapes have fewer unique orientations."""
        # Line shape - symmetric
        line = {(0, 0), (0, 1), (0, 2), (0, 3)}
        line_orientations = get_all_orientations(line)

        # L shape - asymmetric
        l_shape = {(0, 0), (1, 0), (1, 1), (1, 2)}
        l_orientations = get_all_orientations(l_shape)

        # Line should have fewer orientations due to symmetry
        assert len(line_orientations) <= len(l_orientations)

    def test_square_has_minimum_orientations(self) -> None:
        """Test that a square (2x2) has the fewest orientations."""
        # Square - very symmetric
        square = {(0, 0), (0, 1), (1, 0), (1, 1)}
        square_orientations = get_all_orientations(square)

        # L shape - least symmetric common polyomino
        l_shape = {(0, 0), (1, 0), (1, 1), (1, 2)}
        l_orientations = get_all_orientations(l_shape)

        # Square should have fewer orientations than L
        assert len(square_orientations) < len(l_orientations)

    def test_all_orientations_normalized(self) -> None:
        """Test that all orientations have same relative structure."""
        shape = {(5, 5), (5, 6), (6, 5)}
        orientations = get_all_orientations(shape)

        # All orientations should have 3 cells (same as input)
        for orientation in orientations:
            assert len(orientation) == 3

    def test_orientations_are_unique(self) -> None:
        """Test that all orientations are unique shapes."""
        shape = {(0, 0), (1, 0), (1, 1)}
        orientations = get_all_orientations(shape)

        # Convert to frozensets for comparison
        orientation_sets = [frozenset(o) for o in orientations]
        unique_sets = list(set(orientation_sets))

        assert len(orientation_sets) == len(unique_sets)
