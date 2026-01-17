"""Unit tests for validation logic."""

from __future__ import annotations

import pytest

from src.logic.validator import (
    is_contiguous,
    validate_piece_shape,
    validate_piece_placement,
    validate_puzzle_config,
)
from src.models.piece import PuzzlePiece


class TestContiguityValidation:
    """Tests for piece contiguity validation."""

    def test_single_cell_is_contiguous(self) -> None:
        """Test that a single cell is contiguous."""
        shape = {(0, 0)}
        assert is_contiguous(shape) is True

    def test_two_adjacent_cells_are_contiguous(self) -> None:
        """Test that adjacent cells are contiguous."""
        shape = {(0, 0), (0, 1)}
        assert is_contiguous(shape) is True

    def test_L_shape_is_contiguous(self) -> None:
        """Test that L-shaped piece is contiguous."""
        shape = {(0, 0), (1, 0), (1, 1)}
        assert is_contiguous(shape) is True

    def test_disconnected_cells_are_not_contiguous(self) -> None:
        """Test that disconnected cells are not contiguous."""
        shape = {(0, 0), (0, 2)}
        assert is_contiguous(shape) is False

    def test_diagonal_cells_are_not_contiguous(self) -> None:
        """Test that diagonal-only cells are not contiguous."""
        shape = {(0, 0), (1, 1)}
        assert is_contiguous(shape) is False

    def test_complex_shape_is_contiguous(self) -> None:
        """Test that a complex polyomino shape is contiguous."""
        shape = {(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)}  # Cross
        assert is_contiguous(shape) is True

    def test_empty_shape_is_not_contiguous(self) -> None:
        """Test that empty shape is not contiguous."""
        shape = set()
        assert is_contiguous(shape) is False


class TestPieceShapeValidation:
    """Tests for piece shape validation."""

    def test_valid_piece_returns_empty_list(self) -> None:
        """Test that valid piece shape returns empty error list."""
        shape = {(0, 0), (1, 0), (1, 1)}
        errors = validate_piece_shape(shape)
        assert errors == []

    def test_empty_shape_returns_error(self) -> None:
        """Test that empty shape returns validation error."""
        shape = set()
        errors = validate_piece_shape(shape)
        assert len(errors) == 1
        assert "empty" in errors[0].message.lower()

    def test_non_contiguous_shape_returns_error(self) -> None:
        """Test that non-contiguous shape returns validation error."""
        shape = {(0, 0), (0, 2)}
        errors = validate_piece_shape(shape)
        assert len(errors) == 1
        assert "contiguous" in errors[0].message.lower()


class TestPiecePlacementValidation:
    """Tests for piece placement validation."""

    def test_valid_placement_returns_empty(self) -> None:
        """Test that valid placement returns empty error list."""
        piece_shape = {(0, 0), (1, 0)}
        errors = validate_piece_placement(
            piece_shape=piece_shape,
            board_width=5,
            board_height=5,
            position=(0, 0),
        )
        assert errors == []

    def test_out_of_bounds_returns_error(self) -> None:
        """Test that out of bounds placement returns error."""
        piece_shape = {(0, 0), (1, 0), (2, 0)}
        errors = validate_piece_placement(
            piece_shape=piece_shape,
            board_width=3,
            board_height=3,
            position=(2, 2),  # Would go out of bounds
        )
        assert len(errors) >= 1
        assert any("bounds" in e.message.lower() for e in errors)

    def test_placement_on_occupied_cell_returns_error(self) -> None:
        """Test that placement on occupied cell returns error."""
        piece_shape = {(0, 0)}
        occupied = {(0, 0)}
        errors = validate_piece_placement(
            piece_shape=piece_shape,
            board_width=5,
            board_height=5,
            position=(0, 0),
            occupied_cells=occupied,
        )
        assert len(errors) == 1
        assert "occupied" in errors[0].message.lower()


class TestPuzzleConfigValidation:
    """Tests for puzzle config validation."""

    def test_valid_config_returns_empty(self) -> None:
        """Test that valid configuration returns empty error list."""
        piece1 = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})
        piece2 = PuzzlePiece(name="I", shape={(0, 0), (0, 1), (0, 2), (0, 3)})
        pieces = [piece1, piece2]

        errors = validate_puzzle_config(pieces, board_width=6, board_height=6)
        assert errors == []

    def test_duplicate_piece_names_returns_error(self) -> None:
        """Test that duplicate piece names return validation error."""
        piece1 = PuzzlePiece(name="same-name", shape={(0, 0)})
        # Create a second piece with same name but different shape
        piece2 = PuzzlePiece(name="same-name", shape={(0, 0), (1, 0)})
        pieces = [piece1, piece2]

        errors = validate_puzzle_config(pieces, board_width=5, board_height=5)
        assert len(errors) >= 1
        error_messages = [e.message.lower() for e in errors]
        assert any("duplicate" in msg or "name" in msg for msg in error_messages)

    def test_empty_pieces_list_returns_error(self) -> None:
        """Test that empty pieces list returns validation error."""
        errors = validate_puzzle_config([], board_width=5, board_height=5)
        assert len(errors) >= 1
        assert "piece" in errors[0].message.lower()

    def test_piece_area_exceeds_board_returns_error(self) -> None:
        """Test that piece area exceeding board returns error."""
        piece = PuzzlePiece(
            name="large", shape={(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)}
        )
        pieces = [piece]

        errors = validate_puzzle_config(pieces, board_width=3, board_height=3)
        assert len(errors) >= 1
        error_messages = [e.message.lower() for e in errors]
        assert any("area" in msg or "exceed" in msg for msg in error_messages)

    def test_invalid_board_dimensions_returns_error(self) -> None:
        """Test that invalid board dimensions return validation error."""
        piece = PuzzlePiece(name="test", shape={(0, 0)})
        pieces = [piece]

        errors = validate_puzzle_config(pieces, board_width=0, board_height=5)
        assert len(errors) >= 1
        assert (
            "width" in errors[0].message.lower() or "board" in errors[0].message.lower()
        )
