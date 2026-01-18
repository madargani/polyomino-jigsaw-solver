"""File I/O operations for puzzle persistence."""

from __future__ import annotations

import json
from pathlib import Path

from src.models.puzzle_config import PuzzleConfiguration


def save_puzzle(config: PuzzleConfiguration, filepath: Path) -> None:
    """Save puzzle configuration to JSON file.

    Args:
        config: Puzzle configuration to save
        filepath: Output file path (expected to be in ~/.polyomino-puzzles/saved/)

    Raises:
        IOError: If file cannot be written
    """
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = config.to_dict()

        with filepath.open("w") as f:
            json.dump(data, f, indent=2)

    except OSError as e:
        raise OSError(f"Failed to save puzzle to {filepath}: {e}") from e


def load_puzzle(filepath: Path) -> PuzzleConfiguration:
    """Load puzzle configuration from JSON file.

    Args:
        filepath: Input file path (expected to be in ~/.polyomino-puzzles/saved/)

    Returns:
        Loaded PuzzleConfiguration

    Raises:
        IOError: If file cannot be read
        ValueError: If file contains invalid data
    """
    try:
        if not filepath.exists():
            raise OSError(f"File not found: {filepath}")

        with filepath.open("r") as f:
            data = json.load(f)

        return PuzzleConfiguration.from_dict(data)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {filepath}: {e}") from e
    except OSError as e:
        raise OSError(f"Failed to load puzzle from {filepath}: {e}") from e


def export_puzzle(config: PuzzleConfiguration, filepath: Path) -> None:
    """Export puzzle configuration for sharing.

    Args:
        config: Puzzle configuration to export
        filepath: Output file path (user-specified location)

    Raises:
        IOError: If file cannot be written
    """
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = config.to_dict()

        with filepath.open("w") as f:
            json.dump(data, f, indent=2)

    except OSError as e:
        raise OSError(f"Failed to export puzzle to {filepath}: {e}") from e


def import_puzzle(filepath: Path) -> PuzzleConfiguration:
    """Import puzzle configuration from file.

    Args:
        filepath: Input file path (user-specified location)

    Returns:
        Imported PuzzleConfiguration

    Raises:
        IOError: If file cannot be read
        ValueError: If file contains invalid data
    """
    try:
        if not filepath.exists():
            raise OSError(f"File not found: {filepath}")

        with filepath.open("r") as f:
            data = json.load(f)

        return PuzzleConfiguration.from_dict(data)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {filepath}: {e}") from e
    except OSError as e:
        raise OSError(f"Failed to import puzzle from {filepath}: {e}") from e
