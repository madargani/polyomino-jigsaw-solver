"""Saved puzzles tab component for the puzzle editor.

This module contains the SavedPuzzlesTab class which provides a UI for
viewing and managing saved puzzle files.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

SAVED_PUZZLES_DIR = Path.home() / ".polyomino-puzzles" / "saved"


class SavedPuzzlesTab(QWidget):
    """Tab widget for viewing and managing saved puzzles.

    Signals:
        puzzle_selected: Emitted when a puzzle is selected (double-clicked)
        puzzle_deleted: Emitted when a puzzle is deleted
        refresh_requested: Emitted when the list should be refreshed
    """

    # Signals
    puzzle_selected = Signal(Path)
    puzzle_deleted = Signal(Path)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        on_puzzle_selected: Callable[[Path], None] | None = None,
        on_puzzle_deleted: Callable[[Path], None] | None = None,
    ) -> None:
        """Initialize the saved puzzles tab.

        Args:
            parent: Parent widget
            on_puzzle_selected: Callback when a puzzle is selected (double-clicked)
            on_puzzle_deleted: Callback when a puzzle is deleted
        """
        super().__init__(parent)

        self._puzzle_selected_callback = on_puzzle_selected
        self._puzzle_deleted_callback = on_puzzle_deleted

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel("Saved Puzzles")
        header_label.setFont(QFont("", weight=QFont.Weight.Bold, pointSize=14))
        layout.addWidget(header_label)

        instructions = QLabel(
            "Double-click a puzzle to load it.\n"
            "Use File > Save to add puzzles to this list."
        )
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions)

        self._saved_puzzles_list = QListWidget()
        self._saved_puzzles_list.setSelectionMode(
            QListWidget.SelectionMode.SingleSelection
        )
        self._saved_puzzles_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._saved_puzzles_list)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)

        self._refresh_btn = QPushButton("Refresh List")
        self._refresh_btn.clicked.connect(self.refresh)
        button_layout.addWidget(self._refresh_btn)

        self._delete_btn = QPushButton("Delete Selected")
        self._delete_btn.clicked.connect(self._on_delete_clicked)
        button_layout.addWidget(self._delete_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on a puzzle item."""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if filepath:
            self.puzzle_selected.emit(Path(filepath))
            if self._puzzle_selected_callback:
                self._puzzle_selected_callback(Path(filepath))

    def _on_delete_clicked(self) -> None:
        """Handle delete button click."""
        current_item = self._saved_puzzles_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a puzzle to delete.",
            )
            return

        filepath = current_item.data(Qt.ItemDataRole.UserRole)
        if not filepath:
            return

        reply = QMessageBox.question(
            self,
            "Delete Puzzle",
            f"Delete puzzle '{filepath.stem}'?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                Path(filepath).unlink()
                self.puzzle_deleted.emit(Path(filepath))
                if self._puzzle_deleted_callback:
                    self._puzzle_deleted_callback(Path(filepath))
                self.refresh()
            except OSError as e:
                QMessageBox.critical(
                    self,
                    "Delete Failed",
                    f"Failed to delete puzzle:\n{e}",
                )

    def refresh(self) -> None:
        """Refresh the list of saved puzzles."""
        self._saved_puzzles_list.clear()

        if not SAVED_PUZZLES_DIR.exists():
            return

        for filepath in sorted(SAVED_PUZZLES_DIR.glob("*.json")):
            item = QListWidgetItem(filepath.stem)
            item.setData(Qt.ItemDataRole.UserRole, filepath)
            self._saved_puzzles_list.addItem(item)
