"""EditorWindow class for the Polyomino Puzzle Solver application.

This module provides the main editor window with a tabbed interface for
defining puzzle pieces and board configurations.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtGui import QAction, QColor, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.gui.board_tab import BoardTab
from src.gui.piece_tab import PieceTab
from src.models.piece import PuzzlePiece
from src.models.puzzle_config import PuzzleConfiguration
from src.utils.color_generator import get_piece_color


class EditorWindow(QMainWindow):
    """Main editor window for the Polyomino Puzzle Solver.

    Attributes:
        config: The current puzzle configuration being edited
        board_tab: Tab for editing board dimensions and blocked cells
        piece_tab: Tab for drawing piece shapes
        piece_list: List widget showing defined pieces
    """

    def __init__(self) -> None:
        """Initialize the editor window."""
        super().__init__()
        self.setWindowTitle("Polyomino Puzzle Solver")
        self.setMinimumSize(QSize(800, 600))
        self._config = PuzzleConfiguration(
            name="New Puzzle",
            board_width=5,
            board_height=5,
            pieces={},
            blocked_cells=set(),
        )
        self._piece_colors: dict[str, tuple[int, int, int]] = {}
        self._selected_piece_index: int | None = None

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_status_bar()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self._tab_widget = QTabWidget()
        self._tab_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self._tab_widget)

        # Create tabs
        self._piece_tab = PieceTab()
        self._board_tab = BoardTab()

        self._tab_widget.addTab(self._piece_tab, "Pieces")
        self._tab_widget.addTab(self._board_tab, "Board")

        # Piece list panel at bottom
        piece_list_container = QWidget()
        piece_list_layout = QHBoxLayout(piece_list_container)
        piece_list_layout.setContentsMargins(10, 5, 10, 5)

        piece_list_label = QLabel("Defined Pieces:")
        piece_list_label.setFont(QFont("", weight=QFont.Weight.Bold))
        piece_list_layout.addWidget(piece_list_label)

        self._piece_list = QListWidget()
        self._piece_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._piece_list.setMaximumHeight(120)
        piece_list_layout.addWidget(self._piece_list)

        main_layout.addWidget(piece_list_container)

        # Bottom button bar
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 5, 10, 10)

        # Add piece button
        self._add_piece_btn = QPushButton("Add Piece")
        self._add_piece_btn.setMinimumWidth(100)
        button_layout.addWidget(self._add_piece_btn)

        # Delete piece button
        self._delete_piece_btn = QPushButton("Delete Piece")
        self._delete_piece_btn.setMinimumWidth(100)
        button_layout.addWidget(self._delete_piece_btn)

        # Spacer
        button_layout.addStretch()

        # Validation status label
        self._validation_label = QLabel("")
        self._validation_label.setStyleSheet("color: orange;")
        button_layout.addWidget(self._validation_label)

        main_layout.addWidget(button_container)

        # Initialize board
        self._update_board()

    def _setup_menu(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Puzzle", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_puzzle)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)

        load_action = QAction("Load", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._on_load)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        export_action = QAction("Export...", self)
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)

        import_action = QAction("Import...", self)
        import_action.triggered.connect(self._on_import)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self._on_clear)
        edit_menu.addAction(clear_action)

        # Solve menu
        solve_menu = menubar.addMenu("Solve")

        solve_action = QAction("Solve", self)
        solve_action.setShortcut("Ctrl+Enter")
        solve_action.triggered.connect(self._on_solve)
        solve_menu.addAction(solve_action)

    def _setup_toolbar(self) -> None:
        """Set up the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New button
        new_btn = QAction("New", self)
        new_btn.triggered.connect(self._on_new_puzzle)
        toolbar.addAction(new_btn)

        toolbar.addSeparator()

        # Solve button
        solve_btn = QAction("Solve", self)
        solve_btn.triggered.connect(self._on_solve)
        toolbar.addAction(solve_btn)

    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # Add piece button
        self._add_piece_btn.clicked.connect(self._on_add_piece)

        # Delete piece button
        self._delete_piece_btn.clicked.connect(self._on_delete_piece)

        # Piece list selection
        self._piece_list.currentRowChanged.connect(self._on_piece_selected)

        # Board tab signals
        self._board_tab.dimensions_changed.connect(self._on_board_dimensions_changed)
        self._board_tab.blocked_cells_changed.connect(self._on_blocked_cells_changed)

        # Piece tab signals
        self._piece_tab.piece_added.connect(self._on_piece_added)
        self._piece_tab.piece_deleted.connect(self._on_piece_deleted)

    @property
    def config(self) -> PuzzleConfiguration:
        """Get the current puzzle configuration."""
        return self._config

    def _update_board(self) -> None:
        """Update the board tab with current configuration."""
        self._board_tab.set_dimensions(
            self._config.board_width, self._config.board_height
        )
        self._board_tab.set_blocked_cells(self._config.blocked_cells)

    def _update_piece_list(self) -> None:
        """Update the piece list widget."""
        self._piece_list.clear()

        for piece, count in self._config.pieces.items():
            # Generate color for this piece type
            if piece.name not in self._piece_colors:
                color = get_piece_color(len(self._piece_colors))
                self._piece_colors[piece.name] = (
                    color.red(),
                    color.green(),
                    color.blue(),
                )

            item = QListWidgetItem(f"{piece.name} (×{count})")
            item.setData(Qt.ItemDataRole.UserRole, piece.name)

            # Set color indicator
            color = self._piece_colors[piece.name]
            item.setBackground(QColor(*color))

            self._piece_list.addItem(item)

        self._update_validation()

    def _update_validation(self) -> None:
        """Update validation status display."""
        # Get piece area and board area
        piece_area = self._config.get_piece_area()
        board_area = self._config.get_board_area() - len(self._config.blocked_cells)

        if len(self._config.pieces) == 0:
            self._validation_label.setText("No pieces defined")
            self._validation_label.setStyleSheet("color: orange;")
        elif piece_area > board_area:
            self._validation_label.setText(
                f"Warning: Piece area ({piece_area}) exceeds "
                f"available board area ({board_area})"
            )
            self._validation_label.setStyleSheet("color: red;")
        elif piece_area < board_area:
            self._validation_label.setText(
                f"Note: Piece area ({piece_area}) is less than "
                f"board area ({board_area})"
            )
            self._validation_label.setStyleSheet("color: blue;")
        else:
            self._validation_label.setText("Configuration valid")
            self._validation_label.setStyleSheet("color: green;")

    def _on_add_piece(self) -> None:
        """Handle add piece button click."""
        # Get shape from piece tab
        shape = self._piece_tab.get_current_shape()

        if not shape:
            QMessageBox.warning(
                self,
                "No Shape",
                "Please draw a piece shape on the grid first.",
            )
            return

        # Create new piece with unique name
        piece_count = len(
            [p for p in self._config.pieces if p.name.startswith("Piece")]
        )
        piece_name = f"Piece {piece_count + 1}"

        new_piece = PuzzlePiece(name=piece_name, shape=shape)

        # Add to configuration
        self._config.add_piece(new_piece)

        # Update piece list
        self._update_piece_list()

        self._status_bar.showMessage(f"Added piece: {piece_name}")

    def _on_delete_piece(self) -> None:
        """Handle delete piece button click."""
        current_row = self._piece_list.currentRow()

        if current_row < 0:
            QMessageBox.warning(
                self, "No Selection", "Please select a piece to delete."
            )
            return

        # Get piece name from item
        item = self._piece_list.item(current_row)
        piece_name = item.data(Qt.ItemDataRole.UserRole)

        # Find and remove the piece
        for piece in list(self._config.pieces.keys()):
            if piece.name == piece_name:
                self._config.remove_piece(piece)
                break

        # Update piece list
        self._update_piece_list()

        self._status_bar.showMessage(f"Deleted piece: {piece_name}")

    def _on_piece_selected(self, row: int) -> None:
        """Handle piece selection in the list."""
        if row < 0:
            self._selected_piece_index = None
            return

        item = self._piece_list.item(row)
        piece_name = item.data(Qt.ItemDataRole.UserRole)

        # Find the piece and display it
        for piece in self._config.pieces:
            if piece.name == piece_name:
                self._selected_piece_index = row
                break

    def _on_board_dimensions_changed(self, width: int, height: int) -> None:
        """Handle board dimension changes."""
        # Create new configuration with updated dimensions
        self._config = PuzzleConfiguration(
            name=self._config.name,
            board_width=width,
            board_height=height,
            pieces=self._config.pieces.copy(),
            blocked_cells=self._board_tab.blocked_cells,
        )

        self._update_validation()
        self._status_bar.showMessage(f"Board size: {width}×{height}")

    def _on_blocked_cells_changed(self, blocked_cells: set[tuple[int, int]]) -> None:
        """Handle blocked cells changes."""
        # Update configuration
        self._config = PuzzleConfiguration(
            name=self._config.name,
            board_width=self._config.board_width,
            board_height=self._config.board_height,
            pieces=self._config.pieces.copy(),
            blocked_cells=blocked_cells,
        )

        self._update_validation()

    def _on_piece_added(self, piece: PuzzlePiece) -> None:
        """Handle piece added from piece tab."""
        # Sync with our configuration
        self._config.add_piece(piece)
        self._update_piece_list()

    def _on_piece_deleted(self, piece: PuzzlePiece) -> None:
        """Handle piece deleted from piece tab."""
        # Sync with our configuration
        if piece in self._config.pieces:
            self._config.remove_piece(piece)
        self._update_piece_list()

    def _on_new_puzzle(self) -> None:
        """Handle new puzzle action."""
        reply = QMessageBox.question(
            self,
            "New Puzzle",
            "Create a new puzzle? All unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._config = PuzzleConfiguration(
                name="New Puzzle",
                board_width=5,
                board_height=5,
                pieces={},
                blocked_cells=set(),
            )
            self._piece_colors.clear()
            self._update_board()
            self._update_piece_list()
            self._status_bar.showMessage("New puzzle created")

    def _on_save(self) -> None:
        """Handle save action."""
        self._status_bar.showMessage("Save not implemented yet")

    def _on_load(self) -> None:
        """Handle load action."""
        self._status_bar.showMessage("Load not implemented yet")

    def _on_export(self) -> None:
        """Handle export action."""
        self._status_bar.showMessage("Export not implemented yet")

    def _on_import(self) -> None:
        """Handle import action."""
        self._status_bar.showMessage("Import not implemented yet")

    def _on_clear(self) -> None:
        """Handle clear action."""
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Clear all pieces and reset board?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._config = PuzzleConfiguration(
                name=self._config.name,
                board_width=self._config.board_width,
                board_height=self._config.board_height,
                pieces={},
                blocked_cells=self._config.blocked_cells.copy(),
            )
            self._piece_colors.clear()
            self._update_piece_list()
            self._status_bar.showMessage("Cleared all pieces")

    def _on_solve(self) -> None:
        """Handle solve action."""
        self._status_bar.showMessage("Solve not implemented yet")

    def closeEvent(self, event: QEvent) -> None:
        """Handle close event."""
        reply = QMessageBox.question(
            self,
            "Exit",
            "Exit the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            event.ignore()
        else:
            event.accept()
