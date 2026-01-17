"""Integration tests for PuzzleConfiguration."""

from __future__ import annotations

import pytest

from src.models.board import GameBoard
from src.models.piece import PuzzlePiece
from src.models.puzzle_config import PuzzleConfiguration


class TestPuzzleConfigurationCreation:
    """Tests for PuzzleConfiguration creation and initialization."""

    def test_create_config_with_name_and_dimensions(self) -> None:
        """Test creating a basic configuration."""
        config = PuzzleConfiguration(
            name="My Puzzle",
            board_width=5,
            board_height=5,
        )

        assert config.name == "My Puzzle"
        assert config.board_width == 5
        assert config.board_height == 5
        assert len(config.pieces) == 0
        assert len(config.blocked_cells) == 0

    def test_create_config_with_pieces(self) -> None:
        """Test creating configuration with pieces using dict format."""
        piece1 = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})
        piece2 = PuzzlePiece(name="I", shape={(0, 0), (0, 1), (0, 2), (0, 3)})
        config = PuzzleConfiguration(
            name="Test",
            board_width=6,
            board_height=6,
            pieces={piece1: 1, piece2: 1},
        )

        assert len(config.pieces) == 2
        assert config.pieces[piece1] == 1
        assert config.pieces[piece2] == 1

    def test_create_config_with_blocked_cells(self) -> None:
        """Test creating configuration with blocked cells."""
        blocked = {(0, 0), (0, 1), (2, 2)}
        config = PuzzleConfiguration(
            name="Blocked Test",
            board_width=5,
            board_height=5,
            blocked_cells=blocked,
        )

        assert config.blocked_cells == blocked

    def test_create_config_with_piece_counts(self) -> None:
        """Test creating configuration with multiple copies of same piece."""
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})
        config = PuzzleConfiguration(
            name="Multiple Pieces",
            board_width=8,
            board_height=8,
            pieces={piece: 3},
        )

        assert len(config.pieces) == 1
        assert config.pieces[piece] == 3

    def test_empty_name_raises_error(self) -> None:
        """Test that empty puzzle name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            PuzzleConfiguration(
                name="",
                board_width=5,
                board_height=5,
            )

    def test_invalid_dimensions_raise_error(self) -> None:
        """Test that invalid dimensions raise ValueError."""
        with pytest.raises(ValueError, match="width must be between"):
            PuzzleConfiguration(name="Test", board_width=0, board_height=5)

        with pytest.raises(ValueError, match="height must be between"):
            PuzzleConfiguration(name="Test", board_width=5, board_height=51)


class TestPuzzleConfigurationPieceManagement:
    """Tests for adding and removing pieces from configuration."""

    def test_add_piece(self) -> None:
        """Test adding a piece to configuration."""
        config = PuzzleConfiguration(name="Test", board_width=5, board_height=5)
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})

        config.add_piece(piece)

        assert len(config.pieces) == 1
        assert config.pieces[piece] == 1

    def test_add_multiple_copies(self) -> None:
        """Test adding multiple copies of same piece."""
        config = PuzzleConfiguration(name="Test", board_width=10, board_height=10)
        piece = PuzzlePiece(name="monomino", shape={(0, 0)})

        config.add_piece(piece, count=5)

        assert len(config.pieces) == 1
        assert config.pieces[piece] == 5

    def test_add_duplicate_piece_increments_count(self) -> None:
        """Test that adding same piece twice increments count."""
        config = PuzzleConfiguration(name="Test", board_width=5, board_height=5)
        piece = PuzzlePiece(name="test-piece", shape={(0, 0)})

        config.add_piece(piece)
        config.add_piece(piece)

        assert len(config.pieces) == 1
        assert config.pieces[piece] == 2

    def test_remove_piece_decrements_count(self) -> None:
        """Test removing a piece decrements count."""
        config = PuzzleConfiguration(name="Test", board_width=5, board_height=5)
        piece = PuzzlePiece(name="test-piece", shape={(0, 0)})

        config.add_piece(piece, count=3)
        config.remove_piece(piece, count=2)

        assert config.pieces[piece] == 1

    def test_remove_last_piece_removes_entry(self) -> None:
        """Test that removing last piece removes it from dict."""
        config = PuzzleConfiguration(name="Test", board_width=5, board_height=5)
        piece = PuzzlePiece(name="test-piece", shape={(0, 0)})

        config.add_piece(piece)
        config.remove_piece(piece)

        assert piece not in config.pieces

    def test_remove_nonexistent_piece_raises_error(self) -> None:
        """Test that removing non-existent piece raises ValueError."""
        config = PuzzleConfiguration(name="Test", board_width=5, board_height=5)
        piece = PuzzlePiece(name="test", shape={(0, 0)})

        with pytest.raises(ValueError, match="not found"):
            config.remove_piece(piece)


class TestPuzzleConfigurationGetters:
    """Tests for configuration getter methods."""

    def test_get_piece_by_name(self) -> None:
        """Test getting piece by name."""
        piece = PuzzlePiece(name="L-tetromino", shape={(0, 0), (1, 0), (1, 1)})
        config = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece: 1},
        )

        found = config.get_piece_by_name("L-tetromino")
        assert found is not None
        assert found == piece

    def test_get_piece_by_name_returns_none_for_missing(self) -> None:
        """Test that get_piece_by_name returns None for missing piece."""
        config = PuzzleConfiguration(name="Test", board_width=5, board_height=5)

        found = config.get_piece_by_name("nonexistent")
        assert found is None

    def test_get_all_pieces_expands_counts(self) -> None:
        """Test that get_all_pieces returns list with counts expanded."""
        piece1 = PuzzlePiece(name="A", shape={(0, 0)})
        piece2 = PuzzlePiece(name="B", shape={(0, 0)})
        config = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece1: 2, piece2: 3},
        )

        all_pieces = config.get_all_pieces()

        assert len(all_pieces) == 5
        assert all_pieces.count(piece1) == 2
        assert all_pieces.count(piece2) == 3

    def test_get_piece_counts(self) -> None:
        """Test getting piece counts as dict."""
        piece1 = PuzzlePiece(name="A", shape={(0, 0)})
        piece2 = PuzzlePiece(name="B", shape={(0, 0)})
        config = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece1: 2, piece2: 3},
        )

        counts = config.get_piece_counts()

        assert counts == {"A": 2, "B": 3}

    def test_get_board(self) -> None:
        """Test creating GameBoard from configuration."""
        blocked = {(0, 0), (1, 1)}
        config = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            blocked_cells=blocked,
        )

        board = config.get_board()

        assert isinstance(board, GameBoard)
        assert board.width == 5
        assert board.height == 5
        assert board.blocked_cells == blocked


class TestPuzzleConfigurationArea:
    """Tests for area calculation methods."""

    def test_get_total_piece_area(self) -> None:
        """Test calculating total piece area with counts."""
        piece1 = PuzzlePiece(name="monomino", shape={(0, 0)})  # area 1
        piece2 = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})  # area 2
        config = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece1: 3, piece2: 2},
        )

        # 3*1 + 2*2 = 3 + 4 = 7
        assert config.get_total_piece_area() == 7

    def test_get_board_area(self) -> None:
        """Test board area calculation."""
        config = PuzzleConfiguration(name="Test", board_width=6, board_height=4)
        assert config.get_board_area() == 24

    def test_is_solvable_area_true(self) -> None:
        """Test solvable area check when areas match."""
        piece = PuzzlePiece(name="domino", shape={(0, 0), (1, 0)})  # area 2
        config = PuzzleConfiguration(
            name="Test",
            board_width=2,
            board_height=2,
            pieces={piece: 2},
        )

        assert config.is_solvable_area() is True

    def test_is_solvable_area_false(self) -> None:
        """Test solvable area check when areas don't match."""
        piece = PuzzlePiece(name="monomino", shape={(0, 0)})  # area 1
        config = PuzzleConfiguration(
            name="Test",
            board_width=3,
            board_height=3,
            pieces={piece: 5},  # 5 cells, but board has 9
        )

        assert config.is_solvable_area() is False


class TestPuzzleConfigurationValidation:
    """Tests for configuration validation."""

    def test_valid_config_validates(self) -> None:
        """Test that valid configuration passes validation."""
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})
        config = PuzzleConfiguration(
            name="Valid Test",
            board_width=4,
            board_height=3,
            pieces={piece: 4},  # 4 * 3 = 12 cells, board has 16
        )

        errors = config.validate()
        assert len(errors) == 0

    def test_duplicate_piece_names_fails_validation(self) -> None:
        """Test that duplicate piece names fail validation."""
        piece1 = PuzzlePiece(name="same", shape={(0, 0)})
        piece2 = PuzzlePiece(name="same", shape={(0, 0), (1, 0)})
        config = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece1: 1, piece2: 1},
        )

        errors = config.validate()
        error_messages = [e.lower() for e in errors]
        assert any("unique" in msg or "name" in msg for msg in error_messages)

    def test_negative_count_fails_validation(self) -> None:
        """Test that negative piece count fails validation."""
        piece = PuzzlePiece(name="test", shape={(0, 0)})
        config = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece: -1},
        )

        errors = config.validate()
        assert len(errors) >= 1


class TestPuzzleConfigurationSerialization:
    """Tests for configuration serialization (to_dict/from_dict)."""

    def test_to_dict(self) -> None:
        """Test converting configuration to dictionary."""
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})
        config = PuzzleConfiguration(
            name="Test Puzzle",
            board_width=5,
            board_height=5,
            pieces={piece: 2},
            blocked_cells={(0, 0)},
        )

        data = config.to_dict()

        assert data["name"] == "Test Puzzle"
        assert data["board_width"] == 5
        assert data["board_height"] == 5
        assert data["blocked_cells"] == [[0, 0]]
        assert len(data["pieces"]) == 1
        assert data["pieces"][0]["name"] == "L"
        assert data["pieces"][0]["count"] == 2

    def test_from_dict(self) -> None:
        """Test creating configuration from dictionary."""
        data = {
            "name": "Loaded Puzzle",
            "board_width": 6,
            "board_height": 6,
            "blocked_cells": [[0, 0], [1, 1]],
            "pieces": [
                {"name": "L", "shape": [[0, 0], [1, 0], [1, 1]], "count": 2},
                {"name": "I", "shape": [[0, 0], [0, 1], [0, 2]], "count": 1},
            ],
        }

        config = PuzzleConfiguration.from_dict(data)

        assert config.name == "Loaded Puzzle"
        assert config.board_width == 6
        assert config.board_height == 6
        assert len(config.pieces) == 2

    def test_roundtrip_preserves_data(self) -> None:
        """Test that to_dict and from_dict preserve all data."""
        piece = PuzzlePiece(name="Test Piece", shape={(0, 0), (1, 0), (1, 1)})
        config = PuzzleConfiguration(
            name="Roundtrip Test",
            board_width=7,
            board_height=7,
            pieces={piece: 3},
            blocked_cells={(0, 0), (3, 3)},
        )

        # Roundtrip
        data = config.to_dict()
        restored = PuzzleConfiguration.from_dict(data)

        assert restored == config

    def test_from_dict_with_missing_count_defaults_to_1(self) -> None:
        """Test that missing count field defaults to 1."""
        data = {
            "name": "Backward Compatible",
            "board_width": 5,
            "board_height": 5,
            "pieces": [
                {"name": "P", "shape": [[0, 0]]},  # No count field
            ],
        }

        config = PuzzleConfiguration.from_dict(data)
        piece = config.get_piece_by_name("P")

        assert piece is not None
        assert config.pieces[piece] == 1


class TestPuzzleConfigurationCopy:
    """Tests for configuration copying."""

    def test_copy_preserves_state(self) -> None:
        """Test that copy preserves all configuration state."""
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})
        config = PuzzleConfiguration(
            name="Original",
            board_width=5,
            board_height=5,
            pieces={piece: 2},
            blocked_cells={(0, 0)},
        )

        copy = config.copy()

        assert copy.name == config.name
        assert copy.board_width == config.board_width
        assert copy.board_height == config.board_height
        assert copy.blocked_cells == config.blocked_cells
        assert len(copy.pieces) == len(config.pieces)

    def test_copy_is_independent(self) -> None:
        """Test that copy is independent of original."""
        piece = PuzzlePiece(name="L", shape={(0, 0), (1, 0), (1, 1)})
        config = PuzzleConfiguration(
            name="Original",
            board_width=5,
            board_height=5,
            pieces={piece: 1},
        )

        copy = config.copy()

        # Modify original
        config.add_piece(piece)

        # Copy should be unchanged
        assert len(copy.pieces) == 1
        assert len(config.pieces) == 2


class TestPuzzleConfigurationEquality:
    """Tests for configuration equality."""

    def test_equal_configs(self) -> None:
        """Test that identical configurations are equal."""
        piece1 = PuzzlePiece(name="A", shape={(0, 0)})
        piece2 = PuzzlePiece(name="B", shape={(0, 0)})
        config1 = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece1: 1, piece2: 1},
        )
        config2 = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece1: 1, piece2: 1},
        )

        assert config1 == config2

    def test_unequal_configs_different_pieces(self) -> None:
        """Test that configs with different pieces are not equal."""
        piece1 = PuzzlePiece(name="A", shape={(0, 0)})
        piece2 = PuzzlePiece(name="B", shape={(0, 0)})
        config1 = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece1: 1},
        )
        config2 = PuzzleConfiguration(
            name="Test",
            board_width=5,
            board_height=5,
            pieces={piece2: 1},
        )

        assert config1 != config2

    def test_unequal_configs_different_dimensions(self) -> None:
        """Test that configs with different dimensions are not equal."""
        config1 = PuzzleConfiguration(name="Test", board_width=5, board_height=5)
        config2 = PuzzleConfiguration(name="Test", board_width=6, board_height=5)

        assert config1 != config2
