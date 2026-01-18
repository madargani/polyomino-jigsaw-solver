"""PuzzleState class for representing the puzzle solving state."""

from __future__ import annotations

from typing import Any

from src.models.board import GameBoard
from src.models.piece import PuzzlePiece


class PuzzleState:
    """Represents the current state of the solving process.

    Attributes:
        board: Current board configuration
        placed_pieces: List of (piece, position) tuples in placement order
        remaining_pieces: Dictionary of piece to remaining count
        backtrack_history: History of solver operations
    """

    def __init__(
        self,
        board: GameBoard,
        pieces: dict[PuzzlePiece, int],
    ) -> None:
        """Initialize puzzle state with board and pieces.

        Args:
            board: The game board
            pieces: Dictionary mapping piece to count (how many of that piece remain)
        """
        self._board = board
        self._remaining_pieces = pieces.copy()  # Copy to avoid mutation
        self._placed_pieces: list[tuple[PuzzlePiece, tuple[int, int]]] = []
        self._backtrack_history: list[dict[str, Any]] = []

    @property
    def board(self) -> GameBoard:
        """Get the current board."""
        return self._board

    @property
    def placed_pieces(self) -> list[tuple[PuzzlePiece, tuple[int, int]]]:
        """Get list of placed pieces with their positions."""
        return self._placed_pieces.copy()

    @property
    def remaining_pieces(self) -> dict[PuzzlePiece, int]:
        """Get dictionary of remaining pieces with their counts."""
        return self._remaining_pieces.copy()

    @property
    def backtrack_history(self) -> list[dict[str, Any]]:
        """Get history of solver operations."""
        return self._backtrack_history.copy()

    def place_piece(
        self,
        piece: PuzzlePiece,
        position: tuple[int, int],
    ) -> bool:
        """Place a piece and record in state.

        Args:
            piece: The puzzle piece to place
            position: (row, col) position to place piece

        Returns:
            True if piece was placed successfully

        Raises:
            ValueError: If piece cannot be placed or no more of that piece remain
        """
        # Check if we have any of this piece remaining
        if self._remaining_pieces.get(piece, 0) <= 0:
            raise ValueError("No more pieces of this shape remaining")

        if not self._board.can_place_piece(piece, position):
            raise ValueError(f"Cannot place piece at position {position}")

        # Place the piece on the board
        self._board.place_piece(piece, position)

        # Update state
        self._placed_pieces.append((piece, position))

        # Decrement remaining count
        self._remaining_pieces[piece] = self._remaining_pieces.get(piece, 0) - 1
        if self._remaining_pieces[piece] == 0:
            del self._remaining_pieces[piece]

        # Record operation
        self.record_operation("place", str(piece.shape), position, piece)

        return True

    def remove_piece(self, position: tuple[int, int]) -> PuzzlePiece | None:
        """Remove a piece (backtrack).

        Args:
            position: (row, col) position to remove piece from

        Returns:
            The piece that was removed, or None if no piece at position
        """
        # Find the piece at this position
        for i, (piece, pos) in enumerate(self._placed_pieces):
            if pos == position:
                # Remove from board
                self._board.remove_piece(piece, position)
                # Remove from placed pieces
                self._placed_pieces.pop(i)
                # Increment remaining count
                self._remaining_pieces[piece] = self._remaining_pieces.get(piece, 0) + 1
                # Record operation
                self.record_operation("remove", str(piece.shape), position)
                return piece
        return None

    def get_total_remaining_pieces(self) -> int:
        """Get total count of all remaining pieces.

        Returns:
            Sum of all piece counts in remaining_pieces
        """
        return sum(self._remaining_pieces.values())

    def record_operation(
        self,
        operation: str,
        piece_id: str,
        position: tuple[int, int],
        orientation: PuzzlePiece | None = None,
    ) -> None:
        """Record a solver operation for history/visualization.

        Args:
            operation: 'place' or 'remove'
            piece_id: ID of the piece
            position: (row, col) position
            orientation: Piece orientation (for placement)
        """
        entry: dict[str, Any] = {
            "operation": operation,
            "piece_id": piece_id,
            "position": position,
        }
        if orientation is not None:
            entry["orientation"] = {
                "shape": list(orientation.shape),
                "width": orientation.width,
                "height": orientation.height,
            }
        self._backtrack_history.append(entry)

    def get_last_operation(self) -> dict[str, Any] | None:
        """Get the most recent operation.

        Returns:
            Operation dict or None if no operations recorded
        """
        if not self._backtrack_history:
            return None
        return self._backtrack_history[-1].copy()

    def is_solved(self) -> bool:
        """Check if puzzle is solved.

        Returns:
            True if all pieces are placed and board is full
        """
        return len(self._remaining_pieces) == 0 and self._board.is_full()

    def can_proceed(self) -> bool:
        """Check if solving can proceed.

        Returns:
            True if there are pieces left to place
        """
        return len(self._remaining_pieces) > 0

    def copy(self) -> PuzzleState:
        """Create a deep copy of the puzzle state.

        Returns:
            New PuzzleState with identical state
        """
        new_state = PuzzleState(self._board.copy(), self._remaining_pieces.copy())
        new_state._placed_pieces = list(self._placed_pieces)
        new_state._backtrack_history = list(self._backtrack_history)
        return new_state

    def get_statistics(self) -> dict[str, Any]:
        """Get solver statistics.

        Returns:
            Dict with 'placements', 'removals', 'backtracks', etc.
        """
        placements = sum(
            1 for op in self._backtrack_history if op["operation"] == "place"
        )
        removals = sum(
            1 for op in self._backtrack_history if op["operation"] == "remove"
        )
        backtracks = removals

        return {
            "placements": placements,
            "removals": removals,
            "backtracks": backtracks,
            "total_operations": len(self._backtrack_history),
            "pieces_placed": len(self._placed_pieces),
            "pieces_remaining": self.get_total_remaining_pieces(),
        }

    def __repr__(self) -> str:
        """Get string representation."""
        return (
            f"PuzzleState(board={self._board}, "
            f"placed={len(self._placed_pieces)}, "
            f"remaining={self.get_total_remaining_pieces()})"
        )
