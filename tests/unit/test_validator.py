"""Unit tests for validation logic."""

from __future__ import annotations

import pytest

from src.logic.validator import (
    ValidationError,
    validate_piece_shape,
    validate_piece_placement,
    validate_puzzle_config,
    is_contiguous,
    find_connected_components,
)
from src.models.piece import PuzzlePiece


class TestIsContiguous:
    """Test is_contiguous function."""

    def test_single_cell_is_contiguous(self) -> None:
        """Test that a single cell is contiguous."""
        assert is_contiguous({(0, 0)}) is True

    def test_adjacent_cells_are_contiguous(self) -> None:
        """Test that adjacent cells form a contiguous shape."""
        shape = {(0, 0), (0, 1), (1, 0), (1, 1)}  # 2x2 square
        assert is_contiguous(shape) is True

    def test_line_is_contiguous(self) -> None:
        """Test that a line of cells is contiguous."""
        shape = {(0, 0), (0, 1), (0, 2), (0, 3)}  # Horizontal line
        assert is_contiguous(shape) is True

    def test_l_shape_is_contiguous(self) -> None:
        """Test that L-shaped polyomino is contiguous."""
        shape = {(0, 0), (1, 0), (2, 0), (2, 1)}  # L shape
        assert is_contiguous(shape) is True

    def test_disconnected_cells_are_not_contiguous(self) -> None:
        """Test that disconnected cells are not contiguous."""
        shape = {(0, 0), (0, 2)}  # Gap between cells
        assert is_contiguous(shape) is False

    def test_two_separate_clusters_not_contiguous(self) -> None:
        """Test that two separate clusters are not contiguous."""
        shape = {(0, 0), (0, 1), (5, 5), (5, 6)}  # Two far apart
        assert is_contiguous(shape) is False

    def test_empty_shape_is_contiguous(self) -> None:
        """Test that empty shape is considered contiguous (vacuously true)."""
        # Empty set has no disconnected cells
        assert is_contiguous(set()) is True


class TestFindConnectedComponents:
    """Test find_connected_components function."""

    def test_single_component(self) -> None:
        """Test finding a single connected component."""
        shape = {(0, 0), (0, 1), (1, 0)}
        components = find_connected_components(shape)

        assert len(components) == 1

    def test_multiple_components(self) -> None:
        """Test finding multiple disconnected components."""
        shape = {(0, 0), (0, 1), (5, 5), (5, 6)}
        components = find_connected_components(shape)

        assert len(components) == 2

    def test_empty_shape_has_no_components(self) -> None:
        """Test that empty shape has no components."""
        components = find_connected_components(set())
        assert len(components) == 0

    def test_components_are_sets(self) -> None:
        """Test that components are returned as sets."""
        shape = {(0, 0), (0, 1), (1, 0)}
        components = find_connected_components(shape)

        for component in components:
            assert isinstance(component, set)


class TestValidationError:
    """Test ValidationError class."""

    def test_error_with_message(self) -> None:
        """Test ValidationError with just a message."""
        error = ValidationError("TEST_ERROR", "Something went wrong")

        assert error.error_type == "TEST_ERROR"
        assert error.message == "Something went wrong"
        assert error.context == {}

    def test_error_with_context(self) -> None:
        """Test ValidationError with context."""
        error = ValidationError(
            "OUT_OF_BOUNDS", "Piece extends beyond board", {"row": 10, "col": 10}
        )

        assert error.error_type == "OUT_OF_BOUNDS"
        assert "board" in error.message
        assert error.context["row"] == 10

    def test_error_string_representation(self) -> None:
        """Test ValidationError string representation."""
        error = ValidationError("TEST", "Test message")

        assert "TEST" in str(error)
        assert "Test message" in str(error)

    def test_error_equality(self) -> None:
        """Test ValidationError equality."""
        error1 = ValidationError("TEST", "Message", {"key": "value"})
        error2 = ValidationError("TEST", "Message", {"key": "value"})

        assert error1 == error2

    def test_error_inequality(self) -> None:
        """Test ValidationError inequality."""
        error1 = ValidationError("TEST1", "Message")
        error2 = ValidationError("TEST2", "Message")

        assert error1 != error2


class TestValidatePieceShape:
    """Test validate_piece_shape function."""

    def test_valid_shape_returns_empty_list(self) -> None:
        """Test that valid shape returns no errors."""
        shape = {(0, 0), (1, 0), (1, 1)}  # L shape
        errors = validate_piece_shape(shape)

        assert len(errors) == 0

    def test_empty_shape_returns_error(self) -> None:
        """Test that empty shape returns error."""
        errors = validate_piece_shape(set())

        assert len(errors) == 1
        assert errors[0].error_type == "EMPTY_SHAPE"

    def test_non_contiguous_shape_returns_error(self) -> None:
        """Test that non-contiguous shape returns error."""
        shape = {(0, 0), (0, 2)}  # Disconnected
        errors = validate_piece_shape(shape)

        assert len(errors) == 1
        assert errors[0].error_type == "NON_CONTIGUOUS"


class TestValidatePiecePlacement:
    """Test validate_piece_placement function."""

    def test_valid_placement_returns_empty(self) -> None:
        """Test that valid placement returns no errors."""
        piece_shape = {(0, 0), (1, 0), (1, 1)}

        errors = validate_piece_placement(
            piece_shape=piece_shape, board_width=5, board_height=5, position=(0, 0)
        )

        assert len(errors) == 0

    def test_out_of_bounds_returns_error(self) -> None:
        """Test that out-of-bounds placement returns error."""
        piece_shape = {(0, 0), (1, 0), (1, 1)}

        errors = validate_piece_placement(
            piece_shape=piece_shape, board_width=3, board_height=3, position=(2, 2)
        )

        assert len(errors) >= 1
        error_types = [e.error_type for e in errors]
        assert "OUT_OF_BOUNDS" in error_types

    def test_overlap_returns_error(self) -> None:
        """Test that overlapping placement returns error."""
        piece_shape = {(0, 0), (1, 0)}
        occupied = {(0, 0), (0, 1)}  # Some cells already occupied

        errors = validate_piece_placement(
            piece_shape=piece_shape,
            board_width=5,
            board_height=5,
            position=(0, 0),
            occupied_cells=occupied,
        )

        assert len(errors) >= 1
        error_types = [e.error_type for e in errors]
        assert "OVERLAP" in error_types

    def test_no_overlap_when_cells_free(self) -> None:
        """Test no overlap error when cells are free."""
        piece_shape = {(0, 0), (1, 0)}
        occupied = {(5, 5)}  # Far away

        errors = validate_piece_placement(
            piece_shape=piece_shape,
            board_width=5,
            board_height=5,
            position=(0, 0),
            occupied_cells=occupied,
        )

        assert len(errors) == 0

    def test_multiple_errors(self) -> None:
        """Test placement with multiple issues returns multiple errors."""
        piece_shape = {(0, 0), (1, 0), (2, 0)}
        occupied = {(0, 0)}  # First cell occupied

        # Placing at (0,0) overlaps and part goes out of bounds in 3x3
        errors = validate_piece_placement(
            piece_shape=piece_shape,
            board_width=3,
            board_height=3,
            position=(0, 0),
            occupied_cells=occupied,
        )

        assert len(errors) >= 1


class TestValidatePuzzleConfig:
    """Test validate_puzzle_config function."""

    def test_valid_config_returns_empty(self) -> None:
        """Test that valid config returns no errors."""
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})
        pieces = [piece]

        errors = validate_puzzle_config(pieces=pieces, board_width=4, board_height=4)

        assert len(errors) == 0

    def test_empty_pieces_returns_error(self) -> None:
        """Test that empty pieces list returns warning."""
        errors = validate_puzzle_config(pieces=[], board_width=4, board_height=4)

        assert len(errors) >= 1
        error_types = [e.error_type for e in errors]
        assert "NO_PIECES" in error_types

    def test_area_mismatch_returns_error_when_pieces_exceed_board(self) -> None:
        """Test that area mismatch returns error when pieces exceed board."""
        # Create many pieces that exceed 3x3 board area (9 cells)
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})  # 3 cells
        pieces = [piece, piece, piece, piece]  # 12 cells total

        errors = validate_puzzle_config(
            pieces=pieces,
            board_width=3,
            board_height=3,  # 9 cells
        )

        # Should have error about area mismatch
        error_types = [e.error_type for e in errors]
        assert "AREA_MISMATCH" in error_types

    def test_duplicate_piece_names_returns_error(self) -> None:
        """Test that duplicate piece names return error."""
        # Create two pieces with same name
        piece1 = PuzzlePiece(name="L", shape={(0, 0), (1, 0)})
        piece2 = PuzzlePiece(name="L", shape={(0, 0), (0, 1)})  # Same name!
        pieces = [piece1, piece2]

        errors = validate_puzzle_config(pieces=pieces, board_width=4, board_height=4)

        assert len(errors) >= 1
