"""Unit tests for GameBoard class."""

from __future__ import annotations

import pytest

from src.models.board import GameBoard
from src.models.piece import PuzzlePiece


class TestGameBoardCreation:
    """Tests for GameBoard creation and basic properties."""

    def test_create_board_with_dimensions(self) -> None:
        """Test creating a board with width and height."""
        board = GameBoard(width=5, height=5)

        assert board.width == 5
        assert board.height == 5
        assert board.available_area == 25
        assert board.total_area == 25

    def test_create_board_with_blocked_cells(self) -> None:
        """Test creating a board with blocked cells."""
        blocked = {(0, 0), (0, 1), (2, 2)}
        board = GameBoard(width=5, height=5, blocked_cells=blocked)

        assert board.width == 5
        assert board.height == 5
        assert (0, 0) in board.get_blocked_cells()
        assert (0, 1) in board.get_blocked_cells()
        assert (2, 2) in board.get_blocked_cells()

    def test_create_board_invalid_width_raises_error(self) -> None:
        """Test that creating board with invalid width raises ValueError."""
        with pytest.raises(ValueError, match="width must be between 1 and 50"):
            GameBoard(width=0, height=5)

        with pytest.raises(ValueError, match="width must be between 1 and 50"):
            GameBoard(width=51, height=5)

    def test_create_board_invalid_height_raises_error(self) -> None:
        """Test that creating board with invalid height raises ValueError."""
        with pytest.raises(ValueError, match="height must be between 1 and 50"):
            GameBoard(width=5, height=0)

        with pytest.raises(ValueError, match="height must be between 1 and 50"):
            GameBoard(width=5, height=51)

    def test_create_board_blocked_cells_out_of_bounds_raises_error(self) -> None:
        """Test that blocked cells out of bounds raises ValueError."""
        with pytest.raises(ValueError, match="out of board bounds"):
            GameBoard(width=5, height=5, blocked_cells={(10, 10)})


class TestGameBoardProperties:
    """Tests for GameBoard property accessors."""

    def test_total_area(self) -> None:
        """Test total area calculation."""
        board = GameBoard(width=6, height=4)
        assert board.total_area == 24

    def test_available_area_without_blocked(self) -> None:
        """Test available area without blocked cells."""
        board = GameBoard(width=5, height=5)
        assert board.available_area == 25

    def test_available_area_with_blocked(self) -> None:
        """Test available area with blocked cells."""
        blocked = {(0, 0), (0, 1), (1, 0)}
        board = GameBoard(width=5, height=5, blocked_cells=blocked)
        assert board.available_area == 25 - 3


class TestGameBoardPiecePlacement:
    """Tests for piece placement operations."""

    def test_can_place_piece_empty_board(self) -> None:
        """Test checking if piece can be placed on empty board."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        assert board.can_place_piece(piece, (0, 0)) is True

    def test_can_place_piece_out_of_bounds(self) -> None:
        """Test that out of bounds placement returns False."""
        board = GameBoard(width=3, height=3)
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (2, 0)})

        # Try to place at bottom-right corner (would go out of bounds)
        assert board.can_place_piece(piece, (2, 2)) is False

    def test_can_place_piece_on_blocked_cell(self) -> None:
        """Test that placement on blocked cell returns False."""
        board = GameBoard(width=5, height=5, blocked_cells={(1, 1)})
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        assert board.can_place_piece(piece, (1, 1)) is False

    def test_can_place_piece_overlap(self) -> None:
        """Test that overlapping placement returns False."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})

        # Place first piece
        board.place_piece(piece, (0, 0))

        # Try to place overlapping piece
        piece2 = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})
        assert board.can_place_piece(piece2, (0, 0)) is False

    def test_place_piece_success(self) -> None:
        """Test successfully placing a piece."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        result = board.place_piece(piece, (0, 0))

        assert result is True
        assert board.filled_area == 2

    def test_place_piece_returns_false_when_cannot_place(self) -> None:
        """Test that place_piece returns False when placement is invalid."""
        board = GameBoard(width=5, height=5, blocked_cells={(0, 0)})
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        result = board.place_piece(piece, (0, 0))

        assert result is False

    def test_remove_piece(self) -> None:
        """Test removing a piece from the board."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        board.place_piece(piece, (0, 0))
        assert board.filled_area == 2

        board.remove_piece(piece, (0, 0))
        assert board.filled_area == 0

    def test_remove_nonexistent_piece_raises_error(self) -> None:
        """Test that removing non-existent piece raises ValueError."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        with pytest.raises(ValueError, match="No piece at position"):
            board.remove_piece(piece, (0, 0))


class TestGameBoardCellQueries:
    """Tests for board cell query methods."""

    def test_is_cell_filled(self) -> None:
        """Test checking if a cell is filled."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="monomino", shape={(0, 0)})

        assert board.get_piece_at((0, 0)) is None

        board.place_piece(piece, (0, 0))
        assert board.get_piece_at((0, 0)) is not None

    def test_is_cell_blocked(self) -> None:
        """Test checking if a cell is blocked."""
        board = GameBoard(width=5, height=5, blocked_cells={(2, 2)})

        assert board.is_blocked((2, 2)) is True
        assert board.is_blocked((0, 0)) is False

    def test_get_piece_at(self) -> None:
        """Test getting the piece at a specific position."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        assert board.get_piece_at((0, 0)) is None

        board.place_piece(piece, (0, 0))

        # get_piece_at should return the piece's name
        piece_at = board.get_piece_at((0, 0))
        assert piece_at is not None
        # The piece stored at position should match the placed piece's name
        assert piece_at == piece.name

    def test_get_occupied_cells(self) -> None:
        """Test getting all occupied cell positions."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})

        occupied = board.get_occupied_cells()
        assert len(occupied) == 0

        board.place_piece(piece, (0, 0))

        occupied = board.get_occupied_cells()
        assert len(occupied) == 3
        assert (0, 0) in occupied
        assert (1, 0) in occupied
        assert (1, 1) in occupied

    def test_get_empty_cells(self) -> None:
        """Test getting all empty cell positions."""
        board = GameBoard(width=3, height=3)
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        board.place_piece(piece, (0, 0))

        empty = board.get_empty_cells()
        assert len(empty) == 7  # 9 total - 2 occupied
        assert (0, 0) not in empty


class TestGameBoardState:
    """Tests for board state methods."""

    def test_is_empty(self) -> None:
        """Test checking if board is empty."""
        board = GameBoard(width=5, height=5)

        assert board.is_empty() is True

        piece = PuzzlePiece(name="monomino", shape={(0, 0)})
        board.place_piece(piece, (0, 0))

        assert board.is_empty() is False

    def test_is_full(self) -> None:
        """Test checking if board is full."""
        # Create 2x2 board with one monomino
        board = GameBoard(width=2, height=2)
        piece = PuzzlePiece(name="monomino", shape={(0, 0)})

        assert board.is_full() is False

        # Fill the board
        board.place_piece(piece, (0, 0))
        board.place_piece(piece, (0, 1))
        board.place_piece(piece, (1, 0))
        board.place_piece(piece, (1, 1))

        assert board.is_full() is True

    def test_clear(self) -> None:
        """Test clearing the board."""
        board = GameBoard(width=5, height=5, blocked_cells={(0, 0)})
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        board.place_piece(piece, (1, 1))
        assert board.filled_area == 2

        board.clear()
        assert board.filled_area == 0
        # Blocked cells should still be blocked
        assert board.is_blocked((0, 0)) is True


class TestGameBoardCopy:
    """Tests for board copying."""

    def test_copy_preserves_state(self) -> None:
        """Test that copy preserves board state."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        board.place_piece(piece, (0, 0))

        copy = board.copy()

        assert copy.width == board.width
        assert copy.height == board.height
        assert copy.filled_area == board.filled_area
        assert copy.get_occupied_cells() == board.get_occupied_cells()

    def test_copy_is_independent(self) -> None:
        """Test that copy is independent of original."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        board.place_piece(piece, (0, 0))
        copy = board.copy()

        # Modify original
        piece2 = PuzzlePiece(name="monomino", shape={(0, 0)})
        board.place_piece(piece2, (2, 2))

        # Copy should be unchanged
        assert (2, 2) not in copy.get_occupied_cells()


class TestGameBoardComputedProperties:
    """Tests for computed properties."""

    def test_filled_area(self) -> None:
        """Test filled_area property."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})

        assert board.filled_area == 0

        board.place_piece(piece, (0, 0))
        assert board.filled_area == 3

    def test_empty_area(self) -> None:
        """Test empty_area property."""
        board = GameBoard(width=5, height=5, blocked_cells={(0, 0)})
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        assert board.empty_area == 24  # 25 total - 1 blocked

        board.place_piece(piece, (1, 1))
        assert board.empty_area == 22  # 24 - 2 occupied
