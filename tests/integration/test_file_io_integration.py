"""Integration tests for file I/O operations."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.models.puzzle_config import PuzzleConfiguration
from src.models.piece import PuzzlePiece


class TestSaveLoadRoundtrip:
    """Test save/load roundtrip preserves configuration."""

    def test_save_load_preserves_simple_configuration(self) -> None:
        """Test saving and loading preserves simple puzzle configuration."""
        from src.utils.file_io import save_puzzle, load_puzzle

        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        original_config = PuzzleConfiguration(
            name="Simple Puzzle",
            board_width=4,
            board_height=4,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(original_config, filepath)
            loaded_config = load_puzzle(filepath)

            assert loaded_config.name == original_config.name
            assert loaded_config.board_width == original_config.board_width
            assert loaded_config.board_height == original_config.board_height
            assert loaded_config.blocked_cells == original_config.blocked_cells

            loaded_piece = list(loaded_config.pieces.keys())[0]
            original_piece = list(original_config.pieces.keys())[0]

            assert loaded_piece.shape == original_piece.shape
            assert (
                loaded_config.pieces[loaded_piece]
                == original_config.pieces[original_piece]
            )
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_save_load_preserves_complex_configuration(self) -> None:
        """Test saving and loading preserves complex puzzle configuration."""
        from src.utils.file_io import save_puzzle, load_puzzle

        piece1 = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        piece2 = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2), (1, 1)})
        piece3 = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2), (0, 3)})
        blocked_cells = {(0, 0), (2, 2), (3, 3)}
        original_config = PuzzleConfiguration(
            name="Complex Puzzle",
            board_width=5,
            board_height=5,
            pieces={piece1: 2, piece2: 1, piece3: 1},
            blocked_cells=blocked_cells,
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(original_config, filepath)
            loaded_config = load_puzzle(filepath)

            assert loaded_config.name == original_config.name
            assert loaded_config.board_width == original_config.board_width
            assert loaded_config.board_height == original_config.board_height
            assert loaded_config.blocked_cells == original_config.blocked_cells
            assert len(loaded_config.pieces) == len(original_config.pieces)

            # Compare piece counts (compare total counts match)
            original_counts = list(original_config.get_piece_counts().values())
            loaded_counts = list(loaded_config.get_piece_counts().values())
            assert sorted(original_counts) == sorted(loaded_counts)
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_save_load_preserves_piece_shapes(self) -> None:
        """Test saving and loading preserves piece shapes exactly."""
        from src.utils.file_io import save_puzzle, load_puzzle

        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)})
        original_config = PuzzleConfiguration(
            name="Shape Test",
            board_width=6,
            board_height=6,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(original_config, filepath)
            loaded_config = load_puzzle(filepath)

            loaded_piece = list(loaded_config.pieces.keys())[0]
            original_piece = list(original_config.pieces.keys())[0]

            assert loaded_piece.shape == original_piece.shape
            assert len(loaded_piece.shape) == len(original_piece.shape)
            assert loaded_piece.shape == {(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)}
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_save_load_preserves_validation_properties(self) -> None:
        """Test loaded configuration passes validation."""
        from src.utils.file_io import save_puzzle, load_puzzle

        piece = PuzzlePiece(shape={(0, 0), (0, 1)})
        original_config = PuzzleConfiguration(
            name="Valid Puzzle",
            board_width=2,
            board_height=2,
            pieces={piece: 2},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            save_puzzle(original_config, filepath)
            loaded_config = load_puzzle(filepath)

            original_errors = original_config.validate()
            loaded_errors = loaded_config.validate()

            assert original_errors == []
            assert loaded_errors == []
        finally:
            if filepath.exists():
                filepath.unlink()


class TestExportImportRoundtrip:
    """Test export/import roundtrip preserves configuration."""

    def test_export_import_preserves_configuration(self) -> None:
        """Test exporting and importing preserves puzzle configuration."""
        from src.utils.file_io import export_puzzle, import_puzzle

        piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        original_config = PuzzleConfiguration(
            name="Export Test",
            board_width=4,
            board_height=4,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            export_puzzle(original_config, filepath)
            imported_config = import_puzzle(filepath)

            assert imported_config.name == original_config.name
            assert imported_config.board_width == original_config.board_width
            assert imported_config.board_height == original_config.board_height
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_export_import_with_multiple_pieces(self) -> None:
        """Test exporting and importing multiple piece types."""
        from src.utils.file_io import export_puzzle, import_puzzle

        piece1 = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        piece2 = PuzzlePiece(shape={(0, 0), (0, 1), (1, 0), (1, 1)})
        original_config = PuzzleConfiguration(
            name="Multi Export Test",
            board_width=5,
            board_height=5,
            pieces={piece1: 1, piece2: 2},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            export_puzzle(original_config, filepath)
            imported_config = import_puzzle(filepath)

            assert len(imported_config.pieces) == 2
            assert sum(imported_config.pieces.values()) == 3
        finally:
            if filepath.exists():
                filepath.unlink()

    def test_export_import_preserves_piece_properties(self) -> None:
        """Test exporting and importing preserves piece properties."""
        from src.utils.file_io import export_puzzle, import_puzzle

        piece = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2), (1, 1)})
        original_config = PuzzleConfiguration(
            name="Property Test",
            board_width=4,
            board_height=4,
            pieces={piece: 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = Path(f.name)

        try:
            export_puzzle(original_config, filepath)
            imported_config = import_puzzle(filepath)

            imported_piece = list(imported_config.pieces.keys())[0]
            original_piece = list(original_config.pieces.keys())[0]

            assert imported_piece.shape == original_piece.shape
            assert imported_piece.area == original_piece.area
            assert imported_piece.width == original_piece.width
            assert imported_piece.height == original_piece.height
        finally:
            if filepath.exists():
                filepath.unlink()
