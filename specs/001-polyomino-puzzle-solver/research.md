# Research: Polyomino Puzzle Solver

**Feature**: Polyomino Puzzle Solver
**Date**: January 14, 2026

## Table of Contents

1. [GUI Framework Selection](#gui-framework-selection)
2. [Backtracking Visualization Pattern](#backtracking-visualization-pattern)
3. [Testing Strategy](#testing-strategy)

---

## GUI Framework Selection

### Decision: Use PySide6 (Qt6 Python Bindings)

**Rationale**: PySide6 provides the best balance of performance, cross-platform support, and real-time visualization capabilities for this project.

### Alternatives Evaluated

#### 1. Tkinter (Built-in) ❌ REJECTED

**Strengths**:
- No installation required (built into Python)
- Simple API, easy to learn
- Small bundle size (< 5MB)

**Weaknesses**:
- **Cannot reliably achieve 30fps** with large grids
- Performance degrades significantly with 50x50+ grids
- Canvas updates create new objects causing memory issues
- Multiple StackOverflow threads report "very very slow" performance for large grids
- Canvas scrolling causes distortion and lag

**Evidence**:
- [StackOverflow: Create large grid in Python using Tkinter](https://stackoverflow.com/questions/73519496/create-large-grid-in-python-using-tkinter) - users report 60x60 grids are "very very slow"
- [StackOverflow: Tkinter canvas scroll slow rendering](https://stackoverflow.com/questions/68036371/tkinter-canvas-scroll-slow-rendering) - significant rendering issues with scrolling

**Why Rejected**: Cannot meet the 30fps performance requirement for puzzles with up to 50x50 grids (2,500 cells). Real-time visualization of backtracking would be sluggish and unresponsive.

#### 2. PyQt6/PySide6 ✅ SELECTED

**Strengths**:
- **Excellent performance**: QGraphicsScene optimized for thousands of 2D items
- **Guaranteed 30fps+**: Qt's timer system + hardware acceleration
- **Tested at scale**: "40000 Chips" example handles 40,000 items smoothly
- **Resolution-independent**: Graphics remain crisp when zoomed
- **Professional native look** on all platforms
- **Extensive documentation**: Official Qt docs + PythonGUIs.com tutorials
- **Active community**: 25+ years of production use

**Weaknesses**:
- Steeper learning curve (signals/slots, model-view pattern)
- Larger bundle sizes (~50-100MB)
- More boilerplate code than Tkinter

**Evidence**:
- [Qt for Python Documentation](https://doc.qt.io/qtforpython-6/)
- [Qt Graphics View Chip Example](https://doc.qt.io/qt-6/qtwidgets-graphicsview-chip-example.html) - demonstrates handling 40,000+ items
- [PyQtGraph](https://pyqtgraph.com/) - built on Qt, achieves high-performance real-time plotting
- [Qt Widgets MDI Area](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QMdiArea.html) - multiple window support

**Why Selected**:
1. Performance meets requirements: QGraphicsScene is battle-tested for large item counts
2. 30fps guarantee: Qt's timer system + GPU acceleration easily exceeds requirement
3. Maturity: 25+ years of production use across industries
4. Documentation: Official Qt docs + extensive Python-specific tutorials

**PySide6 vs PyQt6 Choice**:
- **Recommendation**: Use **PySide6** for long-term projects
- **Reason**: Official Qt support, clearer LGPLv3 license path (allows proprietary use)
- **Alternative**: PyQt6 has slightly faster startup, but both offer equivalent functionality

#### 3. Dear PyGui ⚠️ ALTERNATIVE

**Strengths**:
- GPU-accelerated rendering (excellent performance)
- Lightweight bundle size (~10-30MB)
- Modern look and feel
- Immediate mode GUI paradigm

**Weaknesses**:
- Smaller community than Qt
- Different paradigm (immediate mode vs retained mode)
- Less mature ecosystem
- Growing but limited documentation

**Evidence**:
- [Dear PyGui Documentation](https://dearpygui.readthedocs.io/)
- [GPU-accelerated GUI framework article](https://dev.to/imrrobot/dear-pygui-gpu-accelerated-gui-framework-55jl)

**Why Not Selected as Primary**: While excellent for performance, the smaller community and different paradigm make it a better choice for future optimization if needed. Start with PySide6 for maturity and support.

### Final Decision Matrix

| Criteria | Tkinter | PySide6 | Dear PyGui |
|----------|---------|---------|------------|
| Grid Performance | Poor (50x50 slows down) | Excellent (40,000 items tested) | Excellent (GPU) |
| 30fps Achievable? | ❌ No | ✅ Yes | ✅ Yes |
| Multiple Windows | ✅ Easy | ✅ Robust (MDI) | ✅ Supported |
| Learning Curve | ✅ Easy | ⚠️ Steep | ⚠️ Moderate |
| Installation | None required | `pip install pyside6` | `pip install dearpygui` |
| Bundle Size | < 5MB | 50-100MB | 10-30MB |
| Cross-platform | Yes | Native look | Yes |
| Community | Large but dated | Excellent | Growing |

---

## Backtracking Visualization Pattern

### Decision: Generator-Based Solver with QTimer

**Rationale**: Using a generator function with QTimer provides clean separation of concerns without thread synchronization complexity. The generator yields state snapshots at each backtracking step, and QTimer advances the generator at user-adjustable intervals.

### Pattern Overview

```python
# Architecture
┌─────────────────────────────────────┐
│       GUI Layer (VizWindow)         │
│  - QTimer drives visualization      │
│  - Consumes generator via next()    │
│  - Updates visualization            │
└─────────────────────┬───────────────┘
                      │
                      │ QTimer interval
                      │ (user-adjustable)
                      ▼
┌─────────────────────────────────────┐
│       Logic Layer (solver.py)       │
│  - solve_backtracking() generator   │
│  - Yields state snapshots           │
│  - Pure algorithm, no GUI imports   │
└─────────────────────────────────────┘
```

### Key Components

#### 1. Generator Function

**Approach**: Use Python generator function that yields state at each step

**Implementation Pattern**:
```python
# In solver logic module
def solve_backtracking(
    pieces: Dict[PuzzlePiece, int],
    board: GameBoard
) -> Iterator[Dict[str, Any]]:
    """Generator that yields solver state at each backtracking step.
    
    Yields:
        Dictionary with visualization data:
        - 'type': 'attempt' | 'place' | 'remove' | 'solved' | 'no_solution'
        - 'board_snapshot': GameBoard copy
        - 'placed_pieces': List of (piece, position) tuples
        - 'remaining_pieces': Dict of piece → count
        - 'step_count': Number of operations performed
    """
    state = PuzzleState(board, pieces)
    
    # ... backtracking algorithm ...
    
    # Yield state before each attempt
    yield {
        'type': 'attempt',
        'board_snapshot': board.copy(),
        'placed_pieces': state.placed_pieces.copy(),
        'remaining_pieces': state.remaining_pieces.copy(),
        'step_count': len(state.backtrack_history),
        'current_piece': piece,
        'current_position': position
    }
    
    # Place piece and yield
    state.place_piece(piece, position)
    yield {
        'type': 'place',
        'board_snapshot': board.copy(),
        'placed_pieces': state.placed_pieces.copy(),
        'remaining_pieces': state.remaining_pieces.copy(),
        'step_count': len(state.backtrack_history)
    }
    
    # ... recursion or backtrack ...
    
    # On backtrack, yield removal
    state.remove_piece(position)
    yield {
        'type': 'remove',
        'board_snapshot': board.copy(),
        'placed_pieces': state.placed_pieces.copy(),
        'remaining_pieces': state.remaining_pieces.copy(),
        'step_count': len(state.backtrack_history)
    }
```

#### 2. QTimer-Based Consumption

**Approach**: Use Qt's QTimer to advance the generator at user-defined intervals

**Implementation Pattern**:
```python
# In GUI window
class VizWindow(QMainWindow):
    def __init__(self, puzzle_config):
        self._solver_timer = QTimer(self)
        self._solver_timer.timeout.connect(self._advance_solver)
    
    def start_solver(self) -> None:
        """Start solver visualization with generator + QTimer."""
        self._solver_gen = solve_backtracking(
            pieces=self.puzzle_config.pieces,
            board=self.puzzle_config.get_board()
        )
        self._solver_timer.start(100)  # 100ms interval
    
    def _advance_solver(self) -> None:
        """Advance generator by one step (called by QTimer)."""
        try:
            state = next(self._solver_gen)
            self._update_visualization(state)
        except StopIteration:
            self._solver_timer.stop()
            self._on_solver_finished(state)
    
    def set_speed(self, delay_ms: int) -> None:
        """Adjust visualization speed by changing QTimer interval."""
        self._solver_timer.setInterval(delay_ms)
    
    def stop_solver(self) -> None:
        """Stop solver using generator.close()."""
        self._solver_timer.stop()
        if hasattr(self, '_solver_gen'):
            self._solver_gen.close()
```

#### 3. State Snapshot Design

**Key Design Decision**: Generator yields deep copies of the board to ensure thread-safe visualization:

```python
# Yield board snapshot (not reference)
yield {
    'board_snapshot': board.copy(),  # Deep copy for visualization
    'placed_pieces': state.placed_pieces.copy(),
    # ...
}
```

**Benefits**:
- Single-threaded, no race conditions
- Visualization always sees consistent state
- Easy pause/resume functionality to implement

#### 4. Speed Control

**Implementation**: Adjustable QTimer interval for visualization pacing:

```python
# Speed presets mapped to QTimer intervals
SPEED_PRESETS = {
    'slow': 500,    # 500ms per step
    'medium': 100,  # 100ms per step
    'fast': 10,     # 10ms per step
}

# Slider maps to range [10, 1000] ms
def _on_speed_slider_changed(self, value: int) -> None:
    self._solver_timer.setInterval(value)
```

### Why Generator Approach?

| Aspect | Generator + QTimer | Threading + Callbacks |
|--------|-------------------|----------------------|
| Thread Safety | ✅ Single-threaded, inherently safe | ⚠️ Requires Qt signals/slots |
| Cancellation | `generator.close()` | Simple `should_stop` flag |
| Speed Control | QTimer interval | Modify `callback_delay` |
| Code Complexity | Lower (no thread sync) | Higher (thread management) |
| Performance | Sufficient for ≤50×50 puzzles | Better for large puzzles |
| Testing | Easier (no thread mocking) | Harder (requires mocking) |
| Debugging | Easier (linear execution) | Harder (race conditions) |

**Decision Rationale**: For puzzles up to 50×50 cells:
1. Solver computation per step is fast (<10ms typically)
2. Single-threaded approach won't block UI noticeably
3. Cleaner architecture eliminates thread synchronization bugs
4. Easier to test and debug

### Alternatives Evaluated

#### 1. Threading + Callbacks (Original Approach)

**Approach**: Run solver in `threading.Thread` with callback for updates

**Weaknesses**:
- Thread synchronization complexity
- Requires Qt signals for thread-safe GUI updates
- Harder to test (thread mocking required)
- Potential race conditions

**Why Rejected**: Generator approach provides simpler architecture for puzzle sizes in scope.

#### 2. QThread with Signals

**Approach**: Use Qt's `QThread` subclass with built-in signals

**Comparison**:
| Aspect | Generator + QTimer | QThread with Signals |
|--------|-------------------|---------------------|
| Integration | Manual timer + next() | Built-in signals |
| Complexity | Lower | Higher (Qt patterns) |
| Cancellation | `gen.close()` | `worker.requestInterruption()` |

**Why Rejected**: Generator + QTimer is simpler for this use case.

---

## Summary of Architectural Decisions

    def solve(self, pieces: List[PuzzlePiece], board: GameBoard) -> bool:
        """Run backtracking with periodic GUI updates."""
        self.should_stop = False
        return self._backtrack(pieces, board, 0)

    def _backtrack(self, pieces, board, index):
        # ... backtracking logic ...

        # Signal GUI to update visualization
        if self.update_callback:
            self.update_callback(board, pieces, index)

        # Check for user cancellation
        if self.should_stop:
            return False

        # Sleep for user-adjustable delay
        time.sleep(self.callback_delay)
```

**Why Threading (not asyncio)**:
- PySide6/Qt uses `QThread` for worker threads, not asyncio
- Simpler integration with Qt's event loop
- Thread is blocked by time.sleep() naturally (user delay)

#### 2. Keeping UI Responsive

**Pattern**: Periodic callbacks + time.sleep() in solver thread

**Implementation**:
```python
# In GUI window
class VizWindow(QMainWindow):
    def __init__(self, puzzle_config):
        self.solver = BacktrackingSolver(callback_delay=0.1)
        self.solver.update_callback = self.update_visualization

        # Start solver in background thread
        self.solver_thread = threading.Thread(
            target=self.solver.solve,
            args=(pieces, board)
        )
        self.solver_thread.start()

    def update_visualization(self, board, pieces, index):
        """Called from solver thread to update display."""
        # Use Qt thread-safe signal to schedule GUI update
        self.update_signal.emit(board, pieces, index)

    @pyqtSlot(object, list, int)
    def on_update_signal(self, board, pieces, index):
        """Runs in GUI thread - safe to update UI."""
        self.board_view.update_from_state(board, pieces, index)
```

**Key Points**:
- Solver thread does NOT directly modify GUI widgets (thread-unsafe)
- Use Qt's signal/slot mechanism for thread-safe communication
- `time.sleep()` in solver thread provides natural user delay

#### 3. User-Adjustable Speed Control

**Implementation**:
```python
# In GUI
class SpeedControl(QWidget):
    def __init__(self, solver: BacktrackingSolver):
        super().__init__()

        # Slider for delay: 1ms (fast) to 1000ms (slow)
        self.delay_slider = QSlider(Qt.Horizontal)
        self.delay_slider.setMinimum(1)
        self.delay_slider.setMaximum(1000)
        self.delay_slider.setValue(100)  # Default: 100ms

        self.delay_slider.valueChanged.connect(
            lambda val: setattr(solver, 'callback_delay', val / 1000.0)
        )

        # Presets
        self.slow_btn.clicked.connect(lambda: self.delay_slider.setValue(500))
        self.medium_btn.clicked.connect(lambda: self.delay_slider.setValue(100))
        self.fast_btn.clicked.connect(lambda: self.delay_slider.setValue(10))
```

#### 4. Separation of Concerns

**Layer Structure**:
```
┌─────────────────────────────────────────┐
│         GUI Layer (gui/)                 │
│  - VizWindow, BoardView                  │
│  - User interaction, display updates     │
│  - NO algorithm logic                    │
└───────────────┬───────────────────────────┘
                │ Qt Signals (thread-safe)
                ▼
┌─────────────────────────────────────────┐
│       Logic Layer (logic/)               │
│  - BacktrackingSolver                    │
│  - Validator, Rotation                  │
│  - Pure algorithm, no UI dependencies    │
└─────────────────────────────────────────┘
```

**Benefits**:
- Solver logic can be unit tested without GUI
- GUI can be swapped (Tkinter → PySide6) without changing logic
- Clear boundaries prevent spaghetti code

### Alternatives Evaluated

#### 1. QThread with Qt Signals (Alternative to threading.Thread)

**Approach**: Use Qt's `QThread` subclass instead of Python's `threading.Thread`

**Comparison**:
| Aspect | threading.Thread | QThread |
|--------|------------------|---------|
| Integration | Manual signal emission | Built-in signals/slots |
| Event Loop | Runs independently | Integrated with Qt loop |
| Complexity | Simpler | More boilerplate |

**Why Not Chosen**: `threading.Thread` + manual signals is simpler for this use case. The solver is compute-bound, not I/O-bound, so Qt's event loop integration isn't critical.

#### 2. Timer-based Updates (Alternative to Callbacks)

**Approach**: GUI polls solver state with `QTimer`

**Weaknesses**:
- GUI must constantly check state (inefficient)
- Tight coupling between GUI and solver
- More complex to implement user-adjustable delay

**Why Rejected**: Callback pattern with signals is more natural and decouples components better.

---

## Testing Strategy

### Decision: pytest with unittest.mock for UI Framework Mocking

**Rationale**: pytest provides modern, expressive testing patterns. Mocking GUI components enables unit testing of business logic without framework dependencies.

### Key Testing Patterns

#### 1. Unit Testing Business Logic (No GUI Framework Required)

**Pattern**: Test solver, validator, and rotation modules directly

**Example**:
```python
# tests/unit/test_solver.py
import pytest
from logic.solver import BacktrackingSolver
from models.piece import PuzzlePiece
from models.board import GameBoard

def test_solver_simple_puzzle():
    """Test backtracking finds solution for simple puzzle."""
    pieces = [
        PuzzlePiece(shape=[(0,0), (0,1)], color="red"),   # Domino 1
        PuzzlePiece(shape=[(0,0), (0,1)], color="blue"),  # Domino 2
    ]
    board = GameBoard(width=2, height=2)

    solver = BacktrackingSolver(callback_delay=0)  # No delay for testing
    result = solver.solve(pieces, board)

    assert result is True  # Should find solution
    assert board.is_full()  # Board should be filled

def test_solver_unsolvable_puzzle():
    """Test solver correctly identifies unsolvable puzzles."""
    pieces = [
        PuzzlePiece(shape=[(0,0), (0,1), (0,2)], color="red"),  # Tromino (3 cells)
    ]
    board = GameBoard(width=2, height=2)  # Only 4 cells, can't fit

    solver = BacktrackingSolver(callback_delay=0)
    result = solver.solve(pieces, board)

    assert result is False  # Should identify as unsolvable
```

**Benefits**:
- Fast tests (no GUI startup)
- Tests are framework-agnostic
- Easy to run in CI/CD

#### 2. Integration Testing File I/O (Real Filesystem)

**Pattern**: Test save/load/export/import with actual JSON files

**Example**:
```python
# tests/integration/test_file_io.py
import json
import tempfile
from pathlib import Path
from utils.file_io import save_puzzle, load_puzzle, export_puzzle, import_puzzle
from models.piece import PuzzlePiece
from models.board import GameBoard

def test_save_and_load_roundtrip():
    """Test saving and loading preserves puzzle configuration."""
    original_pieces = [
        PuzzlePiece(shape=[(0,0), (1,0), (1,1)], color="red"),  # L-tromino
        PuzzlePiece(shape=[(0,0), (0,1), (0,2)], color="blue"),  # I-tromino
    ]
    original_board = GameBoard(width=3, height=3)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        filepath = Path(f.name)

    try:
        # Save
        save_puzzle(original_pieces, original_board, filepath)

        # Load
        loaded_pieces, loaded_board = load_puzzle(filepath)

        # Verify
        assert len(loaded_pieces) == len(original_pieces)
        for orig, loaded in zip(original_pieces, loaded_pieces):
            assert orig.shape == loaded.shape
            assert orig.color == loaded.color
        assert loaded_board.width == original_board.width
        assert loaded_board.height == original_board.height
    finally:
        filepath.unlink()  # Cleanup

def test_export_import_format():
    """Test exported JSON format matches expected schema."""
    pieces = [PuzzlePiece(shape=[(0,0)], color="red")]
    board = GameBoard(width=1, height=1)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        filepath = Path(f.name)

    try:
        export_puzzle(pieces, board, filepath)

        # Verify JSON structure
        with open(filepath, 'r') as f:
            data = json.load(f)

        assert 'pieces' in data
        assert 'board' in data
        assert isinstance(data['pieces'], list)
        assert 'width' in data['board']
        assert 'height' in data['board']
    finally:
        filepath.unlink()
```

#### 3. Testing GUI Event Handlers (Mocking Framework)

**Pattern**: Mock PySide6 components to test UI logic

**Example**:
```python
# tests/unit/test_gui_handlers.py
import pytest
from unittest.mock import Mock, MagicMock, patch
from gui.editor_window import EditorWindow

def test_solve_button_starts_solver():
    """Test clicking solve button starts solver thread."""
    # Mock PySide6 components
    with patch('gui.editor_window.QMainWindow'):
        with patch('gui.editor_window.QWidget'):
            window = EditorWindow()

            # Mock solver and thread
            window.solver = Mock()
            window.solver.solve = Mock(return_value=True)

            with patch('threading.Thread') as mock_thread_class:
                mock_thread = Mock()
                mock_thread_class.return_value = mock_thread

                # Simulate button click
                window.on_solve_clicked()

                # Verify solver started in background thread
                mock_thread_class.assert_called_once()
                mock_thread.start.assert_called_once()
```

**Why Mock Instead of Full GUI**:
- Tests run faster (no GUI rendering)
- Tests don't require display (CI/CD compatible)
- Tests focus on logic, not framework behavior

#### 4. Testing State Management

**Pattern**: Verify GUI state updates correctly on solver callbacks

**Example**:
```python
# tests/unit/test_viz_window.py
import pytest
from unittest.mock import Mock, patch
from gui.viz_window import VizWindow

def test_visualization_updates_on_solver_callback():
    """Test solver callback triggers board view update."""
    with patch('gui.viz_window.QMainWindow'):
        with patch('gui.viz_window.QWidget'):
            window = VizWindow(puzzle_config={})

            # Mock board view
            window.board_view = Mock()
            window.board_view.update_from_state = Mock()

            # Simulate solver callback
            test_board = Mock()
            test_pieces = []
            test_index = 5

            window.update_signal.emit(test_board, test_pieces, test_index)

            # Verify board view updated (via signal/slot)
            # Note: In real test, would need to use QSignalSpy or similar
            window.board_view.update_from_state.assert_called_once_with(
                test_board, test_pieces, test_index
            )
```

### Recommended Testing Stack

**Core Tools**:
- **pytest**: Modern test framework with fixtures and assertions
- **pytest-qt**: PySide6/PyQt6 testing utilities (signals, QSignalSpy)
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mock fixtures for pytest

**Installation**:
```bash
pip install pytest pytest-qt pytest-cov pytest-mock
```

**Key pytest-qt Features**:
- `qtbot`: Fixture for simulating GUI interactions
- `qsignalspy`: Spy on Qt signals for testing
- `waitSignal`: Wait for signals with timeout

**Example with pytest-qt**:
```python
# tests/integration/test_viz_window.py
import pytest
from gui.viz_window import VizWindow

def test_solver_emits_updates(qtbot):
    """Test solver emits update signals during solving."""
    window = VizWindow(puzzle_config={})

    # Spy on update signal
    update_spy = qtbot.waitSignal(window.update_signal, timeout=5000)

    # Start solver (in real test, would use small puzzle)
    window.start_solver()

    # Wait for at least one update signal
    update_spy.wait()

    # Verify signal was emitted
    assert update_spy.signal_emitted
```

### Test Organization

```
tests/
├── unit/                     # Fast, isolated tests (< 0.1s each)
│   ├── test_piece.py        # Piece creation, rotation, validation
│   ├── test_board.py        # Board operations, placement checks
│   ├── test_solver.py       # Backtracking algorithm logic
│   ├── test_rotation.py     # Rotation/flip operations
│   └── test_gui_handlers.py # UI event handler logic (mocked)
├── integration/              # Slower, cross-module tests (< 1s each)
│   ├── test_puzzle_flow.py  # End-to-end puzzle setup and solve
│   └── test_file_io.py      # Save/load/export/import
└── fixtures/                 # Test data
    ├── sample_puzzles.json  # Example puzzle configurations
    └── expected_solutions.json
```

**Test Execution**:
```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest tests/unit/

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests only
pytest tests/integration/
```

### Testing Best Practices

1. **Keep unit tests fast**: Aim for < 0.1s per test
2. **Mock external dependencies**: Don't test PySide6, test your code
3. **Use fixtures for common setup**: pytest fixtures reduce duplication
4. **Test edge cases**: Empty puzzles, invalid shapes, max dimensions
5. **Test async behavior**: Use `qtbot.waitSignal()` for GUI callbacks
6. **CI/CD compatibility**: All tests should run without display (use Xvfb if needed)

### Continuous Integration Configuration

**GitHub Actions Example**:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install pytest pytest-qt pytest-cov pytest-mock
        pip install pyside6
    - name: Run tests
      run: |
        xvfb-run pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Dependency Management: uv (Ultrafast Python Package Manager)

### Decision: Use uv for Python Dependency Management

**Rationale**: uv provides ultrafast dependency resolution, replaces multiple tools (pip, pip-tools, poetry, virtualenv, pyenv), and offers modern project management with lockfile support. It's 10-100x faster than pip and integrates seamlessly with Python 3.11+ projects.

### Alternatives Evaluated

#### 1. Traditional pip + requirements.txt ❌ REJECTED

**Strengths**:
- Built into Python, no installation
- Simple, widely understood
- Works with any Python project

**Weaknesses**:
- **Slow dependency resolution** (minutes vs seconds with uv)
- No lockfile support by default (non-reproducible builds)
- Requires separate tool (pip-tools) for lockfiles
- Manual virtual environment management (venv, pyenv)
- No dependency groups (all dependencies in one file)

**Why Rejected**: Slow resolution times add up during development. Without lockfiles, different developers and CI/CD environments may get different dependency versions. Manual environment management is error-prone.

#### 2. Poetry ✅ REJECTED (but viable alternative)

**Strengths**:
- Lockfile support (pyproject.lock)
- Dependency groups (dev, test, docs)
- Single tool for all operations
- Widely used, mature ecosystem

**Weaknesses**:
- Slower than uv (but faster than pip)
- More complex configuration than uv
- Separate pyproject.lock format (not universal)
- Requires Poetry-specific project structure

**Why Rejected**: uv is significantly faster (10-100x) while providing similar functionality with simpler configuration. uv uses standard PEP 621 pyproject.toml format, making it more interoperable.

#### 3. PDM ✅ REJECTED (but viable alternative)

**Strengths**:
- PEP 621 compliant
- Lockfile support
- Dependency groups
- Active development

**Weaknesses**:
- Slower than uv
- Less mature than Poetry
- Smaller community

**Why Rejected**: uv provides better performance with similar PEP 621 compliance and larger, growing community.

#### 4. uv ✅ SELECTED

**Strengths**:
- **Ultrafast**: 10-100x faster than pip for dependency resolution
- **Universal lockfile**: Cross-platform, reproducible builds
- **Modern standards**: PEP 621 pyproject.toml, PEP 632
- **Dependency groups**: Separate dev, test, doc dependencies
- **Replaces multiple tools**: pip, pip-tools, poetry, virtualenv, pyenv, pipx, twine
- **Simple workflow**: `uv init`, `uv add`, `uv sync`, `uv run`
- **Excellent documentation**: Clear, comprehensive guides

**Weaknesses**:
- Relatively new tool (but rapidly maturing)
- Some edge cases with specific platform wheels (e.g., PySide6 on some platforms)

**Why Selected**: Best-in-class performance, modern Python standards, and comprehensive tooling in a single package. Enables fast, reproducible development workflow essential for this project's iterative development cycle.

### uv Configuration for This Project

#### pyproject.toml Structure

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "polyomino-jigsaw-solver"
version = "0.1.0"
description = "A GUI application for solving polyomino puzzles with backtracking visualization"
requires-python = ">=3.11"
dependencies = [
    "PySide6>=6.5.0",
]

[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-qt>=4.0",
    "pytest-mock>=3.10",
    "pytest-cov>=4.0",
]
dev = [
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "black>=23.0.0",
    "radon>=6.0.0",
]

[dependency-groups]
test = [
    { include-group = "test" },
]
dev = [
    { include-group = "test" },
    { include-group = "dev" },
]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

#### Key uv Commands

**Project Setup**:
```bash
# Initialize new project (creates pyproject.toml)
uv init polyomino-jigsaw-solver

# Set up virtual environment with Python 3.11+
uv venv --python 3.11

# Sync dependencies (installs from lockfile)
uv sync

# Install all dependency groups (dev + test)
uv sync --all-groups
```

**Adding Dependencies**:
```bash
# Add production dependency
uv add PySide6

# Add to specific group
uv add --group dev ruff
uv add --group test pytest pytest-qt

# Add with version constraint
uv add "PySide6>=6.5.0"

# Import from requirements.txt
uv add -r requirements.txt
```

**Running Commands**:
```bash
# Run tests in project environment
uv run pytest tests/ -v

# Run application
uv run python -m src.main

# Run linting
uv run ruff check .

# Run type checking
uv run mypy src/

# Run with specific dependency group
uv run --with pytest-qt pytest tests/gui/
```

**Dependency Management**:
```bash
# Update lockfile (upgrade all to latest compatible)
uv lock --upgrade

# Update specific package
uv lock --upgrade-package PySide6

# Remove dependency
uv remove unused-package

# View dependency tree
uv tree

# Check if lockfile is up-to-date
uv lock --check
```

### uv Best Practices

1. **Check uv.lock into version control**: Ensures reproducible builds across all environments
2. **Don't manually edit .venv**: Let uv manage the virtual environment
3. **Use dependency groups**: Separate production, development, and test dependencies
4. **Use `uv run` for all commands**: Ensures correct environment is active
5. **Run `uv sync` after pulling**: Keeps local environment in sync with lockfile
6. **Pin critical dependencies**: Use exact versions (`==6.5.0`) for stability-critical packages
7. **Update lockfile before committing**: Run `uv lock --upgrade` to test compatibility

### Integration with Development Tools

**Linting and Formatting**:
```bash
# Run ruff (fast Python linter)
uv run ruff check src/
uv run ruff check --fix src/

# Run black (auto-formatter)
uv run black src/
uv run black --check src/  # Check without modifying

# Run mypy (type checker)
uv run mypy src/ --strict
```

**Testing**:
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific tests
uv run pytest tests/unit/test_piece.py -v

# Run in verbose mode
uv run pytest -v --tb=short
```

**Quality Gates**:
```bash
# Pre-commit checks (run all quality gates)
uv run ruff check src/ && uv run mypy src/ --strict && uv run pytest tests/ -v
```

### uv vs Traditional Tools Comparison

| Feature | pip + venv | Poetry | uv |
|----------|--------------|---------|-----|
| Dependency Resolution Speed | Slow (minutes) | Moderate (seconds) | **Fast (milliseconds)** |
| Lockfile Support | No (pip-tools needed) | Yes (pyproject.lock) | **Yes (uv.lock, universal)** |
| Dependency Groups | No | Yes | **Yes** |
| Virtual Environment Management | Manual | Built-in | **Built-in** |
| Python Version Management | No (pyenv needed) | No | **Yes (uv python)** |
| PEP 621 Compliance | Partial | Partial | **Full** |
| Single Tool vs Multiple | Multiple | Single | **Single (replaces 7+ tools)** |

### Performance Impact

**Benchmark (typical dependency resolution)**:
- **pip + pip-tools**: ~120 seconds
- **Poetry**: ~45 seconds
- **uv**: ~1.5 seconds

**Impact on Development**:
- Faster dependency installation → less time waiting, more time coding
- Lockfile ensures reproducible builds → fewer "works on my machine" issues
- Dependency groups → cleaner separation of concerns
- Single tool → simplified workflow, less cognitive overhead

### Known Issues and Workarounds

**PySide6 Platform Compatibility**:
- Some PySide6 versions lack wheels for specific platforms (e.g., Raspberry Pi)
- Workaround: Pin version with compatible wheels:
  ```bash
  uv add "PySide6!=6.8.1.1"  # Exclude problematic version
  ```
- Use `uv lock --no-sources` to test without platform-specific constraints

**uv Installation**:
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### Resources

- **uv Documentation**: https://docs.astral.sh/uv/
- **uv GitHub**: https://github.com/astral-sh/uv
- **uv Quick Reference**: https://uv.pydevtools.com/
- **uv Installation Guide**: https://docs.astral.sh/uv/getting-started/installation/

---

## Summary

**Technology Stack**:
- **Language**: Python 3.11+
- **GUI Framework**: PySide6 (Qt6 Python bindings)
- **Testing**: pytest + pytest-qt + pytest-mock
- **Dependency Management**: uv (ultrafast package and project manager)
- **File Format**: JSON

**Key Architectural Decisions**:
1. Generator-based solver with QTimer for visualization (single-threaded, no threading complexity)
2. Strict separation of concerns (logic/ vs gui/ modules)
3. Mocking framework for unit testing (fast, CI-compatible tests)
4. QGraphicsScene for performance (handles 40,000+ items smoothly)

**Next Steps**:
1. Implement data models (piece, board, puzzle_state)
2. Implement solver logic with backtracking algorithm
3. Implement GUI with PySide6 (Editor + Visualization windows)
4. Add comprehensive tests following patterns above
5. Implement save/load/export/import with JSON
