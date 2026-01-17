"""Main application entry point for the Polyomino Puzzle Solver."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.gui.editor_window import EditorWindow


def main() -> None:
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Polyomino Puzzle Solver")
    app.setApplicationVersion("1.0.0")
    app.setStyle("Fusion")  # Use Fusion style for a clean look

    # Create and show the main editor window
    editor = EditorWindow()
    editor.resize(800, 600)
    editor.show()

    # Run the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
