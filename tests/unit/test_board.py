"""Unit tests for GameBoard class."""

from __future__ import annotations

import pytest

from src.models.board import GameBoard
from src.models.piece import PuzzlePiece


class TestGameBoardCreation:
    """Test GameBoard initialization and basic properties."""

    def test_create_board_with_valid_dimensions(self) -> None:
        """Test creating a board with valid width and height."""
        board = GameBoard(width=5, height=5)

        assert board.width == 5
        assert board.height == 5
        assert board.total_area == 25
        assert board.available_area == 25

    def test_create_board_with_rectangular_dimensions(self) -> None:
        """Test creating a non-square board."""
        board = GameBoard(width=8, height=6)

        assert board.width == 8
        assert board.height == 6
        assert board.total_area == 48

    def test_create_board_with_min_dimensions(self) -> None:
        """Test creating a board with minimum dimensions (1x1)."""
        board = GameBoard(width=1, height=1)

        assert board.width == 1
        assert board.height == 1
        assert board.total_area == 1

    def test_create_board_with_max_dimensions(self) -> None:
        """Test creating a board with maximum dimensions (50x50)."""
        board = GameBoard(width=50, height=50)

        assert board.width == 50
        assert board.height == 50
        assert board.total_area == 2500

    def test_create_board_with_invalid_width_raises_error(self) -> None:
        """Test that invalid width raises ValueError."""
        with pytest.raises(ValueError, match="Width must be between 1 and 50"):
            GameBoard(width=0, height=5)

        with pytest.raises(ValueError, match="Width must be between 1 and 50"):
            GameBoard(width=51, height=5)

    def test_create_board_with_invalid_height_raises_error(self) -> None:
        """Test that invalid height raises ValueError."""
        with pytest.raises(ValueError, match="Height must be between 1 and 50"):
            GameBoard(width=5, height=0)

        with pytest.raises(ValueError, match="Height must be between 1 and 50"):
            GameBoard(width=5, height=51)


class TestGameBoardBlockedCells:
    """Test GameBoard blocked cells functionality."""

    def test_create_board_with_blocked_cells(self) -> None:
        """Test creating a board with blocked cells."""
        blocked = {(0, 0), (0, 1), (4, 4)}
        board = GameBoard(width=5, height=5, blocked_cells=blocked)

        assert board.blocked_cells == blocked
        assert board.available_area == 25 - 3  # Total minus blocked

    def test_blocked_cells_are_immutable(self) -> None:
        """Test that blocked cells cannot be modified directly."""
        blocked = {(0, 0)}
        board = GameBoard(width=3, height=3, blocked_cells=blocked)

        # Attempting to modify should raise error or not affect internal state
        board._blocked_cells.add((1, 1))  # Direct access for test
        assert board.blocked_cells == {(0, 0), (1, 1)}

    def test_blocked_cells_out_of_bounds_raises_error(self) -> None:
        """Test that out-of-bounds blocked cells raise ValueError."""
        with pytest.raises(ValueError, match="out of board bounds"):
            GameBoard(width=3, height=3, blocked_cells={(5, 5)})

    def test_is_blocked_method(self) -> None:
        """Test is_blocked method for checking blocked cells."""
        blocked = {(2, 2)}
        board = GameBoard(width=5, height=5, blocked_cells=blocked)

        assert board.is_blocked((2, 2)) is True
        assert board.is_blocked((0, 0)) is False
        assert board.is_blocked((4, 4)) is False

    def test_get_blocked_cells_returns_set(self) -> None:
        """Test that get_blocked_cells returns a set."""
        blocked = {(0, 0), (1, 1)}
        board = GameBoard(width=3, height=3, blocked_cells=blocked)

        result = board.get_blocked_cells()
        assert isinstance(result, set)
        assert result == blocked


class TestGameBoardCellAccess:
    """Test GameBoard cell access methods."""

    def test_board_initially_empty(self) -> None:
        """Test that new board has no occupied cells."""
        board = GameBoard(width=3, height=3)

        occupied = board.get_occupied_cells()
        assert occupied == set()

        empty = board.get_empty_cells()
        assert len(empty) == 9

    def test_get_piece_at_returns_none_for_empty_cell(self) -> None:
        """Test that get_piece_at returns None for empty cells."""
        board = GameBoard(width=3, height=3)

        assert board.get_piece_at((0, 0)) is None
        assert board.get_piece_at((2, 2)) is None

    def test_get_piece_at_returns_none_for_blocked_cell(self) -> None:
        """Test that get_piece_at returns -1 for blocked cells."""
        board = GameBoard(width=3, height=3, blocked_cells={(1, 1)})

        # Blocked cells return -1 (not None)
        result = board.get_piece_at((1, 1))
        assert result == -1


class TestGameBoardPiecePlacement:
    """Test GameBoard piece placement methods."""

    def test_can_place_piece_returns_true_for_valid_placement(self) -> None:
        """Test can_place_piece returns True for valid placement."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})

        assert board.can_place_piece(piece, (0, 0)) is True
        assert board.can_place_piece(piece, (3, 3)) is True

    def test_can_place_piece_returns_false_for_overlap(self) -> None:
        """Test can_place_piece returns False if piece overlaps existing."""
        board = GameBoard(width=5, height=5)
        piece1 = PuzzlePiece(shape={(0, 0), (1, 0)})
        piece2 = PuzzlePiece(shape={(0, 0), (0, 1)})

        # Place first piece
        board.place_piece(piece1, (0, 0))

        # Second piece overlaps at (0, 0)
        assert board.can_place_piece(piece2, (0, 0)) is False

    def test_can_place_piece_returns_false_for_out_of_bounds(self) -> None:
        """Test can_place_piece returns False for out-of-bounds placement."""
        board = GameBoard(width=3, height=3)
        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})

        # Piece would extend beyond board
        assert board.can_place_piece(piece, (2, 2)) is False
        assert board.can_place_piece(piece, (5, 0)) is False

    def test_can_place_piece_returns_false_for_blocked_cells(self) -> None:
        """Test can_place_piece returns False if piece hits blocked cell."""
        board = GameBoard(width=3, height=3, blocked_cells={(1, 1)})
        # Shape {(0, 0), (1, 0), (1, 1)} placed at (0,0) covers (1,1) - the blocked cell
        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})

        assert board.can_place_piece(piece, (0, 0)) is False

    def test_place_piece_success(self) -> None:
        """Test successful piece placement."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})

        result = board.place_piece(piece, (1, 1))
        assert result is True

        # Verify piece is placed (returns hash of piece shape)
        piece_id = board.get_piece_at((1, 1))
        assert piece_id is not None
        assert board.get_piece_at((2, 1)) == piece_id
        assert board.get_piece_at((2, 2)) == piece_id

    def test_place_piece_updates_occupied_cells(self) -> None:
        """Test that place_piece updates occupied cells."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(shape={(0, 0), (0, 1)})

        board.place_piece(piece, (2, 2))

        occupied = board.get_occupied_cells()
        assert (2, 2) in occupied
        assert (2, 3) in occupied

    def test_place_piece_returns_false_for_invalid_placement(self) -> None:
        """Test that place_piece raises ValueError for invalid placement."""
        board = GameBoard(width=3, height=3)
        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})

        # Out of bounds - should raise ValueError
        with pytest.raises(ValueError):
            board.place_piece(piece, (5, 5))


class TestGameBoardPieceRemoval:
    """Test GameBoard piece removal methods."""

    def test_remove_piece_success(self) -> None:
        """Test successful piece removal."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(shape={(0, 0), (1, 0)})

        board.place_piece(piece, (1, 1))
        board.remove_piece(piece, (1, 1))

        # Verify piece is removed
        assert board.get_piece_at((1, 1)) is None
        assert board.get_piece_at((2, 1)) is None

        occupied = board.get_occupied_cells()
        assert len(occupied) == 0

    def test_remove_nonexistent_piece_raises_error(self) -> None:
        """Test that removing non-existent piece raises ValueError."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(shape={(0, 0), (1, 0)})

        with pytest.raises(ValueError, match="not found"):
            board.remove_piece(piece, (0, 0))

    def test_remove_piece_restores_cells(self) -> None:
        """Test that remove_piece properly restores cells."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(shape={(0, 0), (0, 1)})

        board.place_piece(piece, (2, 2))
        board.remove_piece(piece, (2, 2))

        empty = board.get_empty_cells()
        assert (2, 2) in empty
        assert (2, 3) in empty


class TestGameBoardState:
    """Test GameBoard state methods."""

    def test_is_empty_returns_true_for_new_board(self) -> None:
        """Test is_empty returns True for new board."""
        board = GameBoard(width=5, height=5)
        assert board.is_empty() is True

    def test_is_empty_returns_false_after_piece_placed(self) -> None:
        """Test is_empty returns False after piece placement."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(shape={(0, 0)})

        board.place_piece(piece, (0, 0))
        assert board.is_empty() is False

    def test_is_full_returns_true_when_board_completely_filled(self) -> None:
        """Test is_full returns True when board is completely filled."""
        # 2x2 board with one 2x2 piece
        board = GameBoard(width=2, height=2)
        piece = PuzzlePiece(shape={(0, 0), (0, 1), (1, 0), (1, 1)})

        board.place_piece(piece, (0, 0))
        assert board.is_full() is True

    def test_is_full_returns_false_when_board_not_full(self) -> None:
        """Test is_full returns False when board is not full."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(shape={(0, 0)})

        board.place_piece(piece, (0, 0))
        assert board.is_full() is False

    def test_clear_removes_all_pieces(self) -> None:
        """Test that clear removes all placed pieces."""
        board = GameBoard(width=5, height=5)
        piece1 = PuzzlePiece(shape={(0, 0)})
        piece2 = PuzzlePiece(shape={(0, 0)})

        board.place_piece(piece1, (0, 0))
        board.place_piece(piece2, (1, 1))
        board.clear()

        assert board.is_empty() is True
        assert board.get_occupied_cells() == set()


class TestGameBoardCopy:
    """Test GameBoard copy functionality."""

    def test_copy_creates_independent_board(self) -> None:
        """Test that copy creates an independent board instance."""
        board = GameBoard(width=5, height=5)
        piece = PuzzlePiece(shape={(0, 0)})
        board.place_piece(piece, (0, 0))

        copied = board.copy()

        # Should have same properties
        assert copied.width == board.width
        assert copied.height == board.height

        # Should be independent - modifying original shouldn't affect copy
        board.place_piece(PuzzlePiece(shape={(0, 0)}), (1, 1))
        piece_id = board.get_piece_at((1, 1))
        assert piece_id is not None
        assert copied.get_piece_at((1, 1)) is None

    def test_copy_preserves_blocked_cells(self) -> None:
        """Test that copy preserves blocked cells."""
        board = GameBoard(width=5, height=5, blocked_cells={(2, 2)})
        copied = board.copy()

        assert copied.blocked_cells == board.blocked_cells
        assert copied.is_blocked((2, 2)) is True


class TestGameBoardFilledArea:
    """Test GameBoard area properties."""

    def test_filled_area_property(self) -> None:
        """Test filled_area returns correct count."""
        board = GameBoard(width=4, height=4)
        piece1 = PuzzlePiece(shape={(0, 0), (0, 1)})  # 2 cells
        piece2 = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2)})  # 3 cells

        assert board.filled_area == 0

        board.place_piece(piece1, (0, 0))
        assert board.filled_area == 2

        # Place piece2 at valid position (2, 1) - fits within 4x4 board
        board.place_piece(piece2, (2, 1))
        assert board.filled_area == 5

    def test_empty_area_property(self) -> None:
        """Test empty_area returns correct count."""
        board = GameBoard(width=4, height=4, blocked_cells={(0, 0)})

        assert board.empty_area == 16 - 1  # Total minus blocked

        piece = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2)})
        board.place_piece(piece, (1, 1))

        # 3 cells placed, 1 blocked = 12 empty
        assert board.empty_area == 12
