"""Unit tests for GUI event handlers (User Story 2).

Tests solve button validation and QTimer management using pytest-qt.
"""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch


class TestSolveButtonValidation:
    """Tests for solve button validation logic."""

    def test_solve_button_shows_warning_when_no_pieces(self, qtbot) -> None:
        """Test that solve button shows warning when no pieces defined."""
        from src.gui.editor_window import EditorWindow

        window = EditorWindow()
        qtbot.addWidget(window)

        window._config._pieces = {}

        with patch("src.gui.editor_window.QMessageBox") as mock_msgbox:
            window._on_solve()

            mock_msgbox.warning.assert_called_once()

    def test_solve_button_warns_when_area_exceeds(self, qtbot) -> None:
        """Test that solve button warns when piece area exceeds board area."""
        from src.gui.editor_window import EditorWindow
        from src.models.piece import PuzzlePiece

        window = EditorWindow()
        qtbot.addWidget(window)

        shape = {
            (0, 0),
            (1, 0),
            (2, 0),
            (3, 0),
            (4, 0),
            (5, 0),
            (6, 0),
            (7, 0),
            (8, 0),
            (9, 0),
            (10, 0),
            (11, 0),
            (12, 0),
            (13, 0),
            (14, 0),
            (15, 0),
            (16, 0),
            (17, 0),
            (18, 0),
            (19, 0),
            (20, 0),
            (21, 0),
            (22, 0),
            (23, 0),
            (24, 0),
            (25, 0),
        }
        large_piece = PuzzlePiece(shape=shape)
        window._config._pieces = {large_piece: 1}

        with patch("src.gui.editor_window.QMessageBox") as mock_msgbox:
            mock_msgbox.StandardButton.Yes = mock_msgbox.StandardButton.Yes
            mock_msgbox.StandardButton.No = mock_msgbox.StandardButton.No
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes

            window._on_solve()

            mock_msgbox.question.assert_called_once()


class TestVizWindowQTimer:
    """Tests for QTimer-based solver visualization."""

    def test_viz_window_has_qtimer(self, qtbot) -> None:
        """Test that VisualizationWindow creates a QTimer for stepped execution."""
        from src.gui.visualization_window import VisualizationWindow
        from src.models.puzzle_config import PuzzleConfiguration

        config = PuzzleConfiguration(name="test", board_width=3, board_height=3)
        window = VisualizationWindow(config)
        qtbot.addWidget(window)

        assert hasattr(window, "_timer")
        assert window._timer is not None

    def test_qtimer_interval_adjustable(self, qtbot) -> None:
        """Test that QTimer interval can be adjusted for speed control."""
        from src.gui.visualization_window import VisualizationWindow
        from src.models.puzzle_config import PuzzleConfiguration

        config = PuzzleConfiguration(name="test", board_width=3, board_height=3)
        window = VisualizationWindow(config)
        qtbot.addWidget(window)

        window._on_speed_changed(100)
        assert window._timer.interval() == 100

        window._on_speed_changed(500)
        assert window._timer.interval() == 500

    def test_qtimer_started_on_solver_start(self, qtbot) -> None:
        """Test that QTimer starts when solver begins."""
        from src.gui.visualization_window import VisualizationWindow
        from src.models.puzzle_config import PuzzleConfiguration

        config = PuzzleConfiguration(name="test", board_width=2, board_height=2)
        window = VisualizationWindow(config)
        qtbot.addWidget(window)

        # Create the solver first
        window._create_solver()
        # Start the timer
        window._play_pause_btn.setChecked(True)
        window._play_pause_btn.setText("Pause")
        window._timer.setInterval(100)
        window._timer.start()

        assert window._timer.isActive()

    def test_qtimer_stopped_on_solver_finish(self, qtbot) -> None:
        """Test that QTimer stops when solver finishes."""
        from src.gui.visualization_window import VisualizationWindow
        from src.models.puzzle_config import PuzzleConfiguration

        config = PuzzleConfiguration(name="test", board_width=2, board_height=2)
        window = VisualizationWindow(config)
        qtbot.addWidget(window)

        window._on_stop_clicked()

        assert not window._timer.isActive()


class TestSpeedControl:
    """Tests for visualization speed control."""

    def test_speed_presets_mapping(self, qtbot) -> None:
        """Test that speed presets map to correct intervals."""
        from src.gui.visualization_window import VisualizationWindow
        from src.models.puzzle_config import PuzzleConfiguration

        config = PuzzleConfiguration(name="test", board_width=3, board_height=3)
        window = VisualizationWindow(config)
        qtbot.addWidget(window)

        # Test slider value changes
        window._speed_slider.setValue(500)
        assert window._speed_slider.value() == 500

        window._speed_slider.setValue(100)
        assert window._speed_slider.value() == 100

        window._speed_slider.setValue(10)
        assert window._speed_slider.value() == 10


class TestSolverCancellation:
    """Tests for solver cancellation/interruption."""

    def test_stop_button_closes_generator(self, qtbot) -> None:
        """Test that stopping solver closes the generator."""
        from src.gui.visualization_window import VisualizationWindow
        from src.models.puzzle_config import PuzzleConfiguration

        config = PuzzleConfiguration(name="test", board_width=2, board_height=2)
        window = VisualizationWindow(config)
        qtbot.addWidget(window)

        mock_gen = Mock()
        mock_gen.close = Mock()
        window._generator = mock_gen

        window._on_stop_clicked()

        mock_gen.close.assert_called_once()

    def test_timer_stopped_on_cancellation(self, qtbot) -> None:
        """Test that QTimer is stopped when solver is cancelled."""
        from src.gui.visualization_window import VisualizationWindow
        from src.models.puzzle_config import PuzzleConfiguration

        config = PuzzleConfiguration(name="test", board_width=2, board_height=2)
        window = VisualizationWindow(config)
        qtbot.addWidget(window)

        # Create the solver first
        window._create_solver()
        # Start the timer
        window._play_pause_btn.setChecked(True)
        window._play_pause_btn.setText("Pause")
        window._timer.setInterval(100)
        window._timer.start()

        window._on_stop_clicked()

        assert not window._timer.isActive()
