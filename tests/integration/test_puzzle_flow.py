"""Integration tests for puzzle flow including solving (User Story 2).

Tests the complete puzzle solving workflow from configuration to visualization.
"""

from __future__ import annotations

import pytest

from src.models.piece import PuzzlePiece
from src.models.board import GameBoard
from src.models.puzzle_config import PuzzleConfiguration
from src.logic.solver import solve_backtracking


class TestPuzzleSolveFlow:
    """Integration tests for end-to-end puzzle solving."""

    def test_simple_puzzle_solve_flow(self) -> None:
        """Test complete flow: create puzzle config, get board, solve."""
        # Create pieces
        domino = PuzzlePiece(shape={(0, 0), (0, 1)})

        # Create configuration
        config = PuzzleConfiguration(
            name="Simple Test",
            board_width=2,
            board_height=2,
            pieces={domino: 2},
        )

        # Validate
        errors = config.validate()
        assert len(errors) == 0, f"Configuration should be valid: {errors}"

        # Get board
        board = config.get_board()
        assert board.width == 2
        assert board.height == 2
        assert board.available_area == 4

        # Solve
        generator = solve_backtracking(config.pieces, board)
        yields = list(generator)

        # Verify solver behavior
        assert len(yields) > 0
        last_yield = yields[-1]
        assert last_yield["type"] == "solved"
        assert last_yield["board_snapshot"].is_full()

    def test_no_solution_flow(self) -> None:
        """Test flow for unsolvable puzzle."""
        # Create pieces too large for board
        tromino = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2)})

        config = PuzzleConfiguration(
            name="Impossible",
            board_width=2,
            board_height=2,
            pieces={tromino: 2},  # 6 cells but board only has 4
        )

        # Solve
        board = config.get_board()
        generator = solve_backtracking(config.pieces, board)
        yields = list(generator)

        # Verify no solution
        last_yield = yields[-1]
        assert last_yield["type"] == "no_solution"

    def test_multiple_piece_types_flow(self) -> None:
        """Test solving puzzle with multiple piece types."""
        # Create mixed puzzle: 1 L-tromino + 3 monominoes on 3x2 board
        l_piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})
        monomino = PuzzlePiece(shape={(0, 0)})

        config = PuzzleConfiguration(
            name="Mixed Puzzle",
            board_width=3,
            board_height=2,
            pieces={l_piece: 1, monomino: 3},
        )

        # Validate
        errors = config.validate()
        assert len(errors) == 0

        # Solve
        board = config.get_board()
        generator = solve_backtracking(config.pieces, board)
        yields = list(generator)

        # Should find solution
        last_yield = yields[-1]
        assert last_yield["type"] == "solved"
        assert last_yield["board_snapshot"].is_full()

    def test_solver_yields_state_snapshots(self) -> None:
        """Test that solver yields proper state snapshots for visualization."""
        # Simple solvable puzzle
        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2)
        pieces = {domino: 2}

        generator = solve_backtracking(pieces, board)

        # Collect all snapshots
        snapshots = []
        for state in generator:
            snapshots.append(state)

        # Verify snapshot structure
        assert len(snapshots) > 0
        for snapshot in snapshots:
            # All required keys present
            assert "type" in snapshot
            assert "board_snapshot" in snapshot
            assert "placed_pieces" in snapshot
            assert "remaining_pieces" in snapshot
            assert "step_count" in snapshot

            # Board snapshot is a valid GameBoard
            assert isinstance(snapshot["board_snapshot"], GameBoard)

            # Type is valid
            assert snapshot["type"] in {
                "place",
                "remove",
                "dead_end",
                "solved",
                "no_solution",
            }

    def test_piece_count_tracking(self) -> None:
        """Test that piece counts are properly tracked during solving."""
        # 4 monominoes on 2x2 board
        monomino = PuzzlePiece(shape={(0, 0)})
        board = GameBoard(width=2, height=2)
        pieces = {monomino: 4}

        generator = solve_backtracking(pieces, board)

        # Track remaining pieces across yields
        remaining_counts = []
        for state in generator:
            remaining = state["remaining_pieces"]
            count = sum(remaining.values()) if remaining else 0
            remaining_counts.append(count)

        # Verify count decreases
        assert remaining_counts[-1] == 0  # End with 0

        # Count should be non-increasing
        for i in range(1, len(remaining_counts)):
            assert remaining_counts[i] <= remaining_counts[i - 1]

    def test_blocked_cells_handling(self) -> None:
        """Test solver handles blocked cells correctly."""
        # 2x2 board with one blocked cell, filled with 2 domino halves (monominoes)
        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2, blocked_cells={(0, 0)})

        # Only 3 cells available, need pieces that fit
        monomino = PuzzlePiece(shape={(0, 0)})
        pieces = {monomino: 3}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Should find solution
        last_yield = yields[-1]
        assert last_yield["type"] == "solved"

        # Verify blocked cell remains blocked
        assert last_yield["board_snapshot"].is_blocked((0, 0))
