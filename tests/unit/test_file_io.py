"""Unit tests for file I/O operations."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.models.board import GameBoard
from src.models.puzzle_config import PuzzleConfiguration
from src.models.piece import PuzzlePiece


class TestSavePuzzle:
    """Test save_puzzle function."""

    def test_save_puzzle_creates_json_file(self) -> None:
        """Test saving creates a JSON file with valid structure."""
        from src.utils.file_io import save_puzzle

        piece = PuzzlePiece(name="L-tetromino", shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        config = PuzzleConfiguration(
            name="Test Puzzle",
            board_width=4,
            board_height=4,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(config, filepath)

            assert filepath.exists()

            with filepath.open("r") as f:
                data = json.load(f)

            assert "name" in data
            assert data["name"] == "Test Puzzle"
            assert "board_width" in data
            assert data["board_width"] == 4
            assert "board_height" in data
            assert data["board_height"] == 4
            assert "pieces" in data
            assert len(data["pieces"]) == 1
            assert data["pieces"][0]["name"] == "L-tetromino"
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_save_puzzle_with_multiple_pieces(self) -> None:
        """Test saving configuration with multiple pieces."""
        from src.utils.file_io import save_puzzle

        piece1 = PuzzlePiece(name="L-tetromino", shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        piece2 = PuzzlePiece(name="T-tetromino", shape={(0, 0), (0, 1), (0, 2), (1, 1)})
        config = PuzzleConfiguration(
            name="Multi Piece Puzzle",
            board_width=5,
            board_height=5,
            pieces={piece1: 2, piece2: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(config, filepath)

            with filepath.open("r") as f:
                data = json.load(f)

            assert len(data["pieces"]) == 2
            piece_names = [p["name"] for p in data["pieces"]]
            assert "L-tetromino" in piece_names
            assert "T-tetromino" in piece_names

            l_piece = next(p for p in data["pieces"] if p["name"] == "L-tetromino")
            assert l_piece["count"] == 2
            t_piece = next(p for p in data["pieces"] if p["name"] == "T-tetromino")
            assert t_piece["count"] == 1
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_save_puzzle_with_blocked_cells(self) -> None:
        """Test saving configuration with blocked cells."""
        from src.utils.file_io import save_puzzle

        piece = PuzzlePiece(name="Domino", shape={(0, 0), (0, 1)})
        blocked_cells = {(0, 0), (1, 1)}
        config = PuzzleConfiguration(
            name="Blocked Cells Puzzle",
            board_width=3,
            board_height=3,
            pieces={piece: 3},
            blocked_cells=blocked_cells,
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(config, filepath)

            with filepath.open("r") as f:
                data = json.load(f)

            assert "blocked_cells" in data
            assert len(data["blocked_cells"]) == 2
            assert [0, 0] in data["blocked_cells"]
            assert [1, 1] in data["blocked_cells"]
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_save_puzzle_with_timestamps(self) -> None:
        """Test that timestamps are saved."""
        from src.utils.file_io import save_puzzle
        from datetime import datetime

        piece = PuzzlePiece(name="Monomino", shape={(0, 0)})
        config = PuzzleConfiguration(
            name="Timestamp Puzzle",
            board_width=2,
            board_height=2,
            pieces={piece: 4},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(config, filepath)

            with filepath.open("r") as f:
                data = json.load(f)

            assert "created_at" in data
            assert "modified_at" in data

            created = datetime.fromisoformat(data["created_at"])
            modified = datetime.fromisoformat(data["modified_at"])
            assert isinstance(created, datetime)
            assert isinstance(modified, datetime)
        finally:
            if filepath.exists():
                filepath.unlink()


class TestLoadPuzzle:
    """Test load_puzzle function."""

    def test_load_puzzle_from_valid_file(self) -> None:
        """Test loading a puzzle from a valid JSON file."""
        from src.utils.file_io import save_puzzle, load_puzzle

        piece = PuzzlePiece(name="L-tetromino", shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        original_config = PuzzleConfiguration(
            name="Test Puzzle",
            board_width=4,
            board_height=4,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(original_config, filepath)

            loaded_config = load_puzzle(filepath)

            assert loaded_config.name == "Test Puzzle"
            assert loaded_config.board_width == 4
            assert loaded_config.board_height == 4
            assert len(loaded_config.pieces) == 1
            assert list(loaded_config.pieces.keys())[0].name == "L-tetromino"
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_load_puzzle_with_piece_counts(self) -> None:
        """Test loading preserves piece counts."""
        from src.utils.file_io import save_puzzle, load_puzzle

        piece1 = PuzzlePiece(name="L-tetromino", shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        piece2 = PuzzlePiece(name="T-tetromino", shape={(0, 0), (0, 1), (0, 2), (1, 1)})
        original_config = PuzzleConfiguration(
            name="Count Test",
            board_width=5,
            board_height=5,
            pieces={piece1: 2, piece2: 3},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(original_config, filepath)

            loaded_config = load_puzzle(filepath)

            assert len(loaded_config.pieces) == 2
            for piece, count in loaded_config.pieces.items():
                if piece.name == "L-tetromino":
                    assert count == 2
                elif piece.name == "T-tetromino":
                    assert count == 3
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_load_puzzle_with_blocked_cells(self) -> None:
        """Test loading restores blocked cells."""
        from src.utils.file_io import save_puzzle, load_puzzle

        piece = PuzzlePiece(name="Domino", shape={(0, 0), (0, 1)})
        blocked_cells = {(0, 0), (1, 1)}
        original_config = PuzzleConfiguration(
            name="Blocked Cells Test",
            board_width=3,
            board_height=3,
            pieces={piece: 3},
            blocked_cells=blocked_cells,
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(original_config, filepath)

            loaded_config = load_puzzle(filepath)

            assert loaded_config.blocked_cells == blocked_cells
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_load_puzzle_with_missing_file_raises_error(self) -> None:
        """Test loading from non-existent file raises IOError."""
        from src.utils.file_io import load_puzzle

        with pytest.raises(IOError, match="File not found"):
            load_puzzle(Path("/nonexistent/file.json"))

    def test_load_puzzle_with_invalid_json_raises_error(self) -> None:
        """Test loading from invalid JSON raises ValueError."""
        from src.utils.file_io import load_puzzle

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)
            f.write("{ invalid json }")

        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                load_puzzle(filepath)
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_load_puzzle_with_missing_fields_raises_error(self) -> None:
        """Test loading JSON missing required fields raises ValueError."""
        from src.utils.file_io import load_puzzle

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)
            json.dump({"name": "Incomplete"}, f)

        try:
            with pytest.raises(ValueError, match="Missing required field"):
                load_puzzle(filepath)
        finally:
            if filepath.exists():
                filepath.unlink()


class TestExportPuzzle:
    """Test export_puzzle function."""

    def test_export_puzzle_creates_json_file(self) -> None:
        """Test exporting creates a JSON file."""
        from src.utils.file_io import export_puzzle

        piece = PuzzlePiece(name="L-tetromino", shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        config = PuzzleConfiguration(
            name="Export Test",
            board_width=4,
            board_height=4,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            export_puzzle(config, filepath)

            assert filepath.exists()

            with filepath.open("r") as f:
                data = json.load(f)

            assert "name" in data
            assert data["name"] == "Export Test"
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_export_puzzle_same_as_save(self) -> None:
        """Test that export produces same format as save."""
        from src.utils.file_io import save_puzzle, export_puzzle

        piece = PuzzlePiece(name="T-tetromino", shape={(0, 0), (0, 1), (0, 2), (1, 1)})
        config = PuzzleConfiguration(
            name="Format Test",
            board_width=5,
            board_height=5,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            save_path = Path(f.name)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            export_path = Path(f.name)

        try:
            save_puzzle(config, save_path)
            export_puzzle(config, export_path)

            with save_path.open("r") as f:
                save_data = json.load(f)
            with export_path.open("r") as f:
                export_data = json.load(f)

            assert save_data == export_data
        finally:
            if save_path.exists():
                save_path.unlink()
            if export_path.exists():
                export_path.unlink()


class TestImportPuzzle:
    """Test import_puzzle function."""

    def test_import_puzzle_from_valid_file(self) -> None:
        """Test importing a puzzle from a valid JSON file."""
        from src.utils.file_io import export_puzzle, import_puzzle

        piece = PuzzlePiece(name="L-tetromino", shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        original_config = PuzzleConfiguration(
            name="Import Test",
            board_width=4,
            board_height=4,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            export_puzzle(original_config, filepath)

            imported_config = import_puzzle(filepath)

            assert imported_config.name == "Import Test"
            assert imported_config.board_width == 4
            assert imported_config.board_height == 4
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_import_puzzle_same_as_load(self) -> None:
        """Test that import produces same result as load."""
        from src.utils.file_io import save_puzzle, load_puzzle, import_puzzle

        piece = PuzzlePiece(name="T-tetromino", shape={(0, 0), (0, 1), (0, 2), (1, 1)})
        config = PuzzleConfiguration(
            name="Comparison Test",
            board_width=5,
            board_height=5,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(config, filepath)

            loaded_config = load_puzzle(filepath)
            imported_config = import_puzzle(filepath)

            assert loaded_config.name == imported_config.name
            assert loaded_config.board_width == imported_config.board_width
            assert loaded_config.board_height == imported_config.board_height
        finally:
            if filepath.exists():
                filepath.unlink()
