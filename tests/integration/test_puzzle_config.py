"""Integration tests for puzzle configuration creation and validation."""

from __future__ import annotations

import pytest

from src.models.piece import PuzzlePiece
from src.models.board import GameBoard
from src.models.puzzle_config import PuzzleConfiguration
from src.logic.validator import validate_puzzle_config


class TestPuzzleConfigurationCreation:
    """Integration tests for PuzzleConfiguration creation and validation."""

    def test_create_simple_puzzle_configuration(self) -> None:
        """Test creating a simple valid puzzle configuration."""
        # Create some pieces
        l_piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        t_piece = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2), (1, 1)})

        # Create configuration
        config = PuzzleConfiguration(
            name="Simple Puzzle",
            board_width=4,
            board_height=4,
            pieces={l_piece: 2, t_piece: 1},
        )

        assert config.name == "Simple Puzzle"
        assert config.board_width == 4
        assert config.board_height == 4
        assert len(config.pieces) == 2
        assert config.pieces[l_piece] == 2
        assert config.pieces[t_piece] == 1

    def test_puzzle_configuration_with_blocked_cells(self) -> None:
        """Test creating configuration with blocked cells."""
        piece = PuzzlePiece(shape={(0, 0), (1, 0)})
        blocked = {(1, 1), (1, 2)}

        config = PuzzleConfiguration(
            name="Puzzle with Holes",
            board_width=4,
            board_height=4,
            pieces={piece: 4},
            blocked_cells=blocked,
        )

        assert config.blocked_cells == blocked

    def test_validate_complete_configuration(self) -> None:
        """Test validating a complete puzzle configuration."""
        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})
        config = PuzzleConfiguration(
            name="Test",
            board_width=4,
            board_height=4,
            pieces={piece: 4},  # 4 pieces × 3 cells = 12 cells, fits in 4x4=16
        )

        errors = validate_puzzle_config(
            pieces=list(config.pieces.keys()),
            board_width=config.board_width,
            board_height=config.board_height,
        )

        # Should have no errors (area mismatch not triggered)
        assert len(errors) == 0

    def test_create_board_from_configuration(self) -> None:
        """Test creating a GameBoard from configuration."""
        piece = PuzzlePiece(shape={(0, 0), (1, 0)})
        config = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece: 2},
            blocked_cells={(2, 2)},
        )

        board = config.get_board()

        assert board.width == 5
        assert board.height == 5
        assert board.is_blocked((2, 2)) is True

    def test_get_all_pieces_expands_counts(self) -> None:
        """Test that get_all_pieces expands piece counts."""
        l_piece = PuzzlePiece(shape={(0, 0), (1, 0)})
        t_piece = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2)})

        config = PuzzleConfiguration(
            name="Test", board_width=6, board_height=6, pieces={l_piece: 2, t_piece: 3}
        )

        all_pieces = config.get_all_pieces()

        assert len(all_pieces) == 5  # 2 L's + 3 T's
        assert all_pieces.count(l_piece) == 2
        assert all_pieces.count(t_piece) == 3

    def test_get_piece_counts(self) -> None:
        """Test getting piece shape to count mapping."""
        # Use pieces with different canonical shapes
        domino_piece = PuzzlePiece(shape={(0, 0), (1, 0)})  # 2 cells
        triomino_piece = PuzzlePiece(
            shape={(0, 0), (1, 0), (1, 1)}
        )  # 3 cells (L-shape)

        config = PuzzleConfiguration(
            name="Test",
            board_width=4,
            board_height=4,
            pieces={domino_piece: 3, triomino_piece: 2},
        )

        counts = config.get_piece_counts()

        # Check that we have 2 unique shapes
        assert len(counts) == 2
        # Check the counts (values should be 3 and 2 in some order)
        assert sorted(counts.values()) == [2, 3]

    def test_get_piece_area(self) -> None:
        """Test calculating total piece area."""
        l_piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})  # 4 cells
        i_piece = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2), (0, 3)})  # 4 cells

        config = PuzzleConfiguration(
            name="Test",
            board_width=8,
            board_height=8,
            pieces={l_piece: 2, i_piece: 1},  # 2×4 + 1×4 = 12 cells
        )

        assert config.get_piece_area() == 12

    def test_get_board_area(self) -> None:
        """Test calculating board area."""
        config = PuzzleConfiguration(
            name="Test", board_width=6, board_height=4, pieces={}
        )

        assert config.get_board_area() == 24  # 6 × 4

    def test_is_solvable_area(self) -> None:
        """Test area solvability check."""
        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})  # 3 cells

        # Exact fit
        config1 = PuzzleConfiguration(
            name="Exact",
            board_width=3,
            board_height=3,
            pieces={piece: 3},  # 9 cells total
        )
        assert config1.is_solvable_area() is True

        # Pieces exceed board
        config2 = PuzzleConfiguration(
            name="Too Big",
            board_width=2,
            board_height=2,
            pieces={piece: 2},  # 6 cells, board has 4
        )
        assert config2.is_solvable_area() is False


class TestPuzzleConfigurationModification:
    """Test modifying puzzle configurations."""

    def test_add_piece(self) -> None:
        """Test adding a piece to configuration."""
        piece = PuzzlePiece(shape={(0, 0), (1, 0)})
        config = PuzzleConfiguration(
            name="Test", board_width=4, board_height=4, pieces={}
        )

        config.add_piece(piece, 2)

        assert config.pieces[piece] == 2
        assert config.get_piece_area() == 4  # 2 pieces × 2 cells

    def test_remove_piece(self) -> None:
        """Test removing a piece from configuration."""
        piece = PuzzlePiece(shape={(0, 0), (1, 0)})
        config = PuzzleConfiguration(
            name="Test", board_width=4, board_height=4, pieces={piece: 3}
        )

        config.remove_piece(piece, 2)

        assert config.pieces[piece] == 1

    def test_add_same_piece_increments_count(self) -> None:
        """Test that adding same piece type increments count."""
        piece = PuzzlePiece(shape={(0, 0), (1, 0)})
        config = PuzzleConfiguration(
            name="Test", board_width=4, board_height=4, pieces={piece: 1}
        )

        config.add_piece(piece)

        assert config.pieces[piece] == 2


class TestPuzzleConfigurationSerialization:
    """Test puzzle configuration serialization."""

    def test_to_dict(self) -> None:
        """Test converting configuration to dictionary."""
        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})
        config = PuzzleConfiguration(
            name="Test Puzzle",
            board_width=4,
            board_height=4,
            pieces={piece: 2},
            blocked_cells={(1, 1)},
        )

        data = config.to_dict()

        assert data["name"] == "Test Puzzle"
        assert data["board_width"] == 4
        assert data["board_height"] == 4
        assert len(data["pieces"]) == 1
        # Pieces should have shape and count, but no name
        assert "shape" in data["pieces"][0]
        assert "name" not in data["pieces"][0]
        assert data["pieces"][0]["count"] == 2
        # Blocked cells are serialized as list of lists
        assert [1, 1] in data["blocked_cells"]

    def test_from_dict(self) -> None:
        """Test creating configuration from dictionary."""
        data = {
            "name": "My Puzzle",
            "board_width": 5,
            "board_height": 5,
            "blocked_cells": [[0, 0], [0, 1]],
            "pieces": [{"shape": [[0, 0], [1, 0], [1, 1]], "count": 2}],
            "created_at": "2026-01-14T12:00:00",
            "modified_at": "2026-01-14T12:30:00",
        }

        config = PuzzleConfiguration.from_dict(data)

        assert config.name == "My Puzzle"
        assert config.board_width == 5
        assert config.board_height == 5
        assert len(config.blocked_cells) == 2

    def test_serialization_roundtrip(self) -> None:
        """Test that serialization roundtrip preserves data."""
        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        original = PuzzleConfiguration(
            name="Roundtrip Test",
            board_width=6,
            board_height=6,
            pieces={piece: 3},
            blocked_cells={(2, 2), (3, 3)},
        )

        # Serialize and deserialize
        data = original.to_dict()
        restored = PuzzleConfiguration.from_dict(data)

        assert restored.name == original.name
        assert restored.board_width == original.board_width
        assert restored.board_height == original.board_height
        assert len(restored.pieces) == len(original.pieces)
        assert restored.blocked_cells == original.blocked_cells
