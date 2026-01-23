# Polyomino Puzzle Solver

This Christmas I was gifted the [Aztec Labrinth puzzle](https://www.amazon.com/Bending-Wooden-Labyrinth-Difficult-Puzzles/dp/B08DDFNGV6) by Woodster.

Inspired by day 12 of [Advent of Code 2025](https://adventofcode.com/2025) and my Analysis of Algorithms class, I decided to make a backtracking solver for this puzzle.

![Solver Demo](assets/polyomino_solver.gif)

## Features

- **Puzzle Editor**: Draw polyomino pieces and configure board dimensions
- **Backtracking Solver**: Automatic puzzle solving with step-by-step visualization
- **Real-time Visualization**: Watch the solver place and remove pieces in real-time
- **Speed Control**: Adjustable visualization speed (slow, medium, fast, or custom)
- **Puzzle Management**: Save, load, export, and import puzzle configurations

## Quick Start

### Prerequisites

- Python 3.11 or higher
- uv (ultrafast Python package manager)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd polyomino-jigsaw-solver

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up the project with all dependencies
uv sync --all-groups
```

### Running the Application

```bash
# Launch the puzzle editor
uv run python -m src.main
```

## Usage

### Creating a Puzzle

1. Launch the application
2. Define pieces in the pieces tab
3. Define board size and shape in the board tab

### Solving a Puzzle

1. Define a new puzzle or import an existing puzzle
2. Click "Solve" to open the visualization window
3. Click "Play" to start the solver
4. Adjust speed using the slider or presets

### Saving/Loading

You can save defined puzzles to a JSON file and load them to the solver later.

## Project Structure

```
polyomino-jigsaw-solver/
├── src/
│   ├── main.py             # Application entry point
│   ├── models/             # Data structures
│   │   ├── piece.py        # PuzzlePiece class
│   │   ├── board.py        # GameBoard class
│   │   └── puzzle_config.py # PuzzleConfiguration class
│   ├── logic/              # Business logic
│   │   ├── solver.py       # Backtracking algorithm
│   │   ├── validator.py    # Validation logic
│   │   └── rotation.py     # Rotation/flip operations
│   ├── gui/                # User interface
│   │   ├── editor_window.py    # Main editor window
│   │   ├── board_tab.py        # Board configuration tab
│   │   ├── board_widget.py     # Board grid widget
│   │   ├── piece_tab.py        # Piece editor tab
│   │   ├── saved_puzzles_tab.py # Saved puzzles management
│   │   └── visualization_window.py # Solver visualization
│   └── utils/              # Utilities
│       ├── file_io.py      # JSON I/O
│       ├── formatting.py   # Formatting helpers
│       └── color_generator.py # Color generation utilities
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   │   ├── test_board.py
│   │   ├── test_piece.py
│   │   ├── test_file_io.py
│   │   ├── test_gui_handlers.py
│   │   ├── test_rotation.py
│   │   ├── test_solver.py
│   │   └── test_validator.py
│   └── integration/        # Integration tests
│       ├── test_file_io_integration.py
│       ├── test_puzzle_config.py
│       └── test_puzzle_flow.py
├── specs/                  # Feature specifications
│   └── 001-polyomino-puzzle-solver/
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lockfile
└── README.md               # This file
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_piece.py -v

# Run unit tests only
uv run pytest tests/unit/

# Run integration tests only
uv run pytest tests/integration/
```

### Code Quality

```bash
# Run linter
uv run ruff check src/

# Auto-fix linting issues
uv run ruff check --fix src/

# Run formatter
uv run black src/

# Run type checker
uv run mypy src/ --strict

# Run all quality checks
uv run ruff check src/ && uv run mypy src/ --strict && uv run pytest tests/ -v
```

## Dependencies

- **PySide6**: Qt6 Python bindings for GUI
- **pytest**: Testing framework
- **pytest-qt**: Qt testing utilities
- **pytest-mock**: Mocking utilities
- **uv**: Package manager

## License

MIT License
