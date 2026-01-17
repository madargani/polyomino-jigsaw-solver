# Implementation Plan: Polyomino Puzzle Solver

**Branch**: `001-polyomino-puzzle-solver` | **Date**: January 16, 2026 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-polyomino-puzzle-solver/spec.md`

## Summary

A Python GUI application for solving polyomino puzzles using backtracking algorithm with real-time visualization. The application provides a puzzle editor for defining piece shapes and board configurations, and a separate visualization window showing the step-by-step solving process.

**Technical Approach**:

- **GUI Framework**: PySide6 (Qt6 Python bindings) for high-performance real-time visualization
- **Architecture**: Thread-based solver with Qt signals for thread-safe GUI updates
- **Data Layer**: Immutable models (PuzzlePiece, GameBoard, PuzzleState, PuzzleConfiguration)
- **Testing**: pytest + pytest-qt with mocked GUI components
- **Dependency Management**: uv for fast, reproducible Python package management

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: PySide6>=6.5.0, pytest>=7.0, pytest-qt>=4.0, pytest-mock>=3.10  
**Storage**: JSON file format for puzzle save/load/export/import  
**Testing**: pytest with pytest-qt for GUI testing, pytest-mock for mocking  
**Target Platform**: Desktop (Linux, macOS, Windows)  
**Project Type**: Single desktop application  
**Performance Goals**: 30fps minimum during visualization for puzzles with up to 2500 cells (50×50)  
**Constraints**: <200ms UI response time, offline-capable, no external services  
**Scale/Scope**: Single-user desktop application, typically 1-50 pieces per puzzle

## UI Design Notes

- **Tabbed Interface**: Editor uses separate "Pieces" and "Board" tabs to maximize vertical screen space
- **Auto-resize Grids**: Both piece and board editors automatically resize to fit within visible screen area
- **Consistent Interaction**: Both editors use identical interaction patterns (left-click, drag, right-click)
- **Dynamic Colors**: Piece colors are generated during visualization, not stored with piece definitions

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- **Modularity & Decomposition**: ✅ Files split by responsibility (models/, logic/, gui/, utils/). Functions under 50 lines, files under 300 lines.
- **Readability First**: ✅ All functions have type hints and docstrings. Descriptive naming throughout.
- **GUI Separation of Concerns**: ✅ Business logic separated from UI code (logic/ vs gui/). Thread-based solver prevents GUI blocking.
- **Code Quality Gates**: ✅ Linter (ruff), type checker (mypy), formatter (black) configured in pyproject.toml.
- **Simplicity Over Complexity**: ✅ Minimal dependencies (PySide6 + testing libs). Standard library first approach. No premature optimization.

**Status**: ✅ ALL GATES PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-polyomino-puzzle-solver/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command) ✅ COMPLETE
├── data-model.md        # Phase 1 output (/speckit.plan command) ✅ COMPLETE
├── quickstart.md        # Phase 1 output (/speckit.plan command) ✅ COMPLETE
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── gui-events.json  # Qt signal/slot contracts ✅ COMPLETE
│   ├── json-schema.json # JSON serialization schema ✅ COMPLETE
│   └── module-api.md    # Module API contracts ✅ COMPLETE
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   ├── piece.py         # PuzzlePiece class
│   ├── board.py         # GameBoard class
│   ├── puzzle_state.py  # PuzzleState class
│   └── puzzle_config.py # PuzzleConfiguration class
├── logic/
│   ├── __init__.py
│   ├── solver.py        # BacktrackingSolver class
│   ├── validator.py     # PuzzleValidator class
│   └── rotation.py      # RotationOperations class
├── gui/
│   ├── __init__.py
│   ├── editor_window.py # EditorWindow class with tabbed interface (Pieces/Board tabs)
│   ├── viz_window.py    # VizWindow class
│   ├── board_tab.py     # Tab for editing board
│   └── piece_tab.py     # Tab for editing pieces
├── utils/
│   ├── __init__.py
│   └── file_io.py       # JSON save/load/export/import
├── config.py            # Constants and configuration
└── main.py              # Application entry point

tests/
├── unit/
│   ├── __init__.py
│   ├── test_piece.py
│   ├── test_board.py
│   ├── test_solver.py
│   ├── test_rotation.py
│   └── test_gui_handlers.py
├── integration/
│   ├── __init__.py
│   ├── test_puzzle_flow.py
│   └── test_file_io.py
└── fixtures/
    ├── __init__.py
    └── sample_puzzles.json
```

**Structure Decision**: Single project with clear module boundaries. Models contain pure data structures with no business logic. Logic module contains algorithms (solver, validator, rotation). GUI module contains Qt widgets. Utils module contains file I/O. This separation enables unit testing without GUI dependencies.

## Implementation Phases

### Phase 0: Research (✅ COMPLETE)

- GUI Framework Selection: PySide6 chosen for performance and cross-platform support
- Backtracking Visualization: Thread-based solver with Qt signals
- Testing Strategy: pytest + pytest-qt with mocked GUI components
- Dependency Management: uv for fast Python package management

**Output**: `research.md` (923 lines)

### Phase 1: Design (✅ COMPLETE)

- Data Models: PuzzlePiece, GameBoard, PuzzleState, PuzzleConfiguration
- GUI Event Contracts: Qt signal/slot definitions (gui-events.json)
- JSON Schema: Puzzle configuration file format (json-schema.json)
- Module APIs: Public interfaces between modules (module-api.md)
- Quickstart Guide: Setup and development workflow documentation

**Output**: `data-model.md`, `quickstart.md`, `contracts/*`

### Phase 2: Implementation (PENDING)

- Create source code structure (src/, tests/)
- Implement models (piece, board, puzzle_state, puzzle_config)
- Implement logic (solver, validator, rotation)
- Implement GUI (editor_window, viz_window, board_view, piece_widget)
- Implement utils (file_io)
- Write unit tests
- Write integration tests
- Verify code quality (ruff, mypy, black)
- Test on all target platforms

**Output**: `tasks.md` (generated by /speckit.tasks command)

## Next Steps

1. **Generate Implementation Tasks**: Run `/speckit.tasks` to generate detailed implementation tasks
2. **Review Phase 1 Artifacts**: Verify research.md, data-model.md, quickstart.md, and contracts/\* are complete
3. **Begin Implementation**: Start with models layer, then logic, then GUI
4. **Run Quality Gates**: Ensure ruff, mypy, and tests pass at each milestone
5. **Update Documentation**: Keep spec.md and other documentation in sync with implementation

## Verification Checklist

- [x] Technical Context filled with Python 3.11+, PySide6, pytest, uv
- [x] Constitution Check: All 5 principles pass
- [x] Project Structure: Single project with clear module boundaries defined
- [x] Phase 0 Research: research.md complete (GUI framework, visualization, testing, dependencies)
- [x] Phase 1 Design: data-model.md, quickstart.md, contracts/\* complete
- [x] Agent Context: opencode context updated in AGENTS.md
- [x] All artifacts in correct location: `specs/001-polyomino-puzzle-solver/`

**Plan Status**: ✅ READY FOR IMPLEMENTATION
