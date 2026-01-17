"""EditorWindow - Main puzzle configuration editor window."""

from __future__ import annotations

import uuid

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.gui.board_view import BoardView
from src.gui.piece_widget import PieceWidget, generate_piece_color
from src.models.piece import PuzzlePiece
from src.models.puzzle_config import PuzzleConfiguration
from src.utils.formatting import (
    format_area_comparison,
    format_piece_count,
)


class EditorWindow(QMainWindow):
    """Main window for the puzzle editor.

    Signals:
        config_changed: Emitted when the configuration changes
        solve_requested: Emitted when user clicks solve
    """

    config_changed = Signal(PuzzleConfiguration)
    solve_requested = Signal(PuzzleConfiguration)

    def __init__(self) -> None:
        """Initialize the editor window."""
        super().__init__()
        self._config: PuzzleConfiguration | None = None
        self._selected_piece_name: str | None = None
        self._piece_widgets: dict[str, PieceWidget] = {}
        self._is_solving = False

        self._setup_ui()
        self._create_initial_config()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Polyomino Puzzle Solver")
        self.setMinimumSize(QSize(900, 600))

        # Create central widget with splitter
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Create horizontal splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Piece list and controls
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Board editor
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter sizes (30% left, 70% right)
        splitter.setSizes([300, 700])

        # Create menu bar
        self._create_menu_bar()

        # Create tool bar
        self._create_tool_bar()

        # Status bar
        self.statusBar().showMessage("Ready")

    def _create_left_panel(self) -> QWidget:
        """Create the left panel with piece list and controls.

        Returns:
            Left panel widget
        """
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # Board dimensions section
        dims_label = QLabel("<b>Board Dimensions</b>")
        layout.addWidget(dims_label)

        dims_layout = QHBoxLayout()
        width_label = QLabel("Width:")
        self._width_spin = QComboBox()
        self._width_spin.addItems([str(i) for i in range(1, 51)])
        self._width_spin.setCurrentText("5")
        self._width_spin.currentTextChanged.connect(self._on_board_dimension_changed)

        height_label = QLabel("Height:")
        self._height_spin = QComboBox()
        self._height_spin.addItems([str(i) for i in range(1, 51)])
        self._height_spin.setCurrentText("5")
        self._height_spin.currentTextChanged.connect(self._on_board_dimension_changed)

        dims_layout.addWidget(width_label)
        dims_layout.addWidget(self._width_spin)
        dims_layout.addWidget(height_label)
        dims_layout.addWidget(self._height_spin)
        layout.addLayout(dims_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Pieces section
        pieces_label = QLabel("<b>Pieces</b>")
        layout.addWidget(pieces_label)

        # Piece count label
        self._piece_count_label = QLabel("0 pieces")
        layout.addWidget(self._piece_count_label)

        # Piece list
        self._piece_list = QListWidget()
        self._piece_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._piece_list.itemClicked.connect(self._on_piece_selected)
        self._piece_list.itemDoubleClicked.connect(self._on_piece_double_clicked)
        layout.addWidget(self._piece_list)

        # Piece controls
        piece_buttons_layout = QHBoxLayout()

        add_piece_btn = QPushButton("Add Piece")
        add_piece_btn.clicked.connect(self._on_add_piece)
        piece_buttons_layout.addWidget(add_piece_btn)

        delete_piece_btn = QPushButton("Delete")
        delete_piece_btn.clicked.connect(self._on_delete_piece)
        piece_buttons_layout.addWidget(delete_piece_btn)

        layout.addLayout(piece_buttons_layout)

        # Separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)

        # Piece Editor section
        piece_editor_label = QLabel("<b>Edit Selected Piece</b>")
        layout.addWidget(piece_editor_label)

        # Piece editor instructions
        piece_instructions = QLabel(
            "Click on cells to add/remove.\nRight-click to remove cells."
        )
        piece_instructions.setStyleSheet(
            "color: #666; font-style: italic; font-size: 11px;"
        )
        layout.addWidget(piece_instructions)

        # Piece editor widget container
        self._piece_editor_container = QFrame()
        self._piece_editor_container.setFrameStyle(QFrame.Shape.Box)
        self._piece_editor_container.setLineWidth(1)
        piece_editor_layout = QVBoxLayout(self._piece_editor_container)
        piece_editor_layout.setContentsMargins(5, 5, 5, 5)

        # Piece name label
        self._piece_name_label = QLabel("<i>No piece selected</i>")
        self._piece_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        piece_editor_layout.addWidget(self._piece_name_label)

        # Piece editor widget
        self._piece_editor = PieceWidget()
        self._piece_editor.setVisible(False)
        self._piece_editor.shape_changed.connect(self._on_piece_shape_changed)
        piece_editor_layout.addWidget(self._piece_editor)

        layout.addWidget(self._piece_editor_container)

        # Separator
        line3 = QFrame()
        line3.setFrameShape(QFrame.Shape.HLine)
        line3.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line3)

        # Area info
        area_label = QLabel("<b>Area</b>")
        layout.addWidget(area_label)

        self._area_label = QLabel("0 / 25 cells")
        layout.addWidget(self._area_label)

        # Spacer
        layout.addStretch()

        return panel

    def _create_right_panel(self) -> QWidget:
        """Create the right panel with the board editor.

        Returns:
            Right panel widget
        """
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # Board editor label
        label = QLabel("<b>Board Editor</b>")
        layout.addWidget(label)

        # Instructions
        instructions = QLabel(
            "Click to fill cells. Drag to paint. Right-click to toggle. "
            "Set board dimensions on the left."
        )
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions)

        # Board view
        self._board_view = BoardView(width=5, height=5, cell_size=40)
        self._board_view.cell_toggled.connect(self._on_board_cell_toggled)
        layout.addWidget(self._board_view)

        # Board controls
        board_controls = QHBoxLayout()

        clear_board_btn = QPushButton("Clear Board")
        clear_board_btn.clicked.connect(self._on_clear_board)
        board_controls.addWidget(clear_board_btn)

        set_blocked_btn = QPushButton("Set Blocked Cells")
        set_blocked_btn.clicked.connect(self._on_set_blocked_cells)
        board_controls.addWidget(set_blocked_btn)

        layout.addLayout(board_controls)

        # Spacer
        layout.addStretch()

        return panel

    def _create_menu_bar(self) -> None:
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Puzzle", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_puzzle)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        save_action = QAction("Save...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_puzzle)
        file_menu.addAction(save_action)

        load_action = QAction("Load...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._on_load_puzzle)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        export_action = QAction("Export...", self)
        export_action.triggered.connect(self._on_export_puzzle)
        file_menu.addAction(export_action)

        import_action = QAction("Import...", self)
        import_action.triggered.connect(self._on_import_puzzle)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        clear_action = QAction("Clear All", self)
        clear_action.setShortcut("Ctrl+Del")
        clear_action.triggered.connect(self._on_clear_all)
        edit_menu.addAction(clear_action)

        # Puzzle menu
        puzzle_menu = menubar.addMenu("Puzzle")

        solve_action = QAction("Solve", self)
        solve_action.setShortcut("Ctrl+Enter")
        solve_action.triggered.connect(self._on_solve)
        puzzle_menu.addAction(solve_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _create_tool_bar(self) -> None:
        """Create the tool bar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New button
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self._on_new_puzzle)
        toolbar.addWidget(new_btn)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._on_save_puzzle)
        toolbar.addWidget(save_btn)

        # Load button
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._on_load_puzzle)
        toolbar.addWidget(load_btn)

        toolbar.addSeparator()

        # Solve button
        solve_btn = QPushButton("Solve")
        solve_btn.clicked.connect(self._on_solve)
        toolbar.addWidget(solve_btn)

        toolbar.addSeparator()

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._on_clear_all)
        toolbar.addWidget(clear_btn)

    def _create_initial_config(self) -> None:
        """Create an initial empty puzzle configuration."""
        try:
            self._config = PuzzleConfiguration(
                name="New Puzzle",
                board_width=5,
                board_height=5,
            )
            self._update_ui_from_config()
        except ValueError:
            # Fallback if there's an issue
            self._config = None
            QMessageBox.warning(
                self,
                "Error",
                "Failed to create initial configuration. Please restart the application.",
            )

    def _create_piece(self, name: str = "") -> PuzzlePiece:
        """Create a new puzzle piece.

        Args:
            name: Optional piece name

        Returns:
            New PuzzlePiece instance
        """
        piece_name = name if name else f"piece-{uuid.uuid4().hex[:8]}"
        # Start with a simple 1x1 piece
        shape = {(0, 0)}
        return PuzzlePiece(name=piece_name, shape=shape)

    def _add_piece_to_config(self, piece: PuzzlePiece, count: int = 1) -> None:
        """Add a piece to the configuration and UI.

        Args:
            piece: PuzzlePiece to add
            count: Number of copies to add
        """
        if self._config is None:
            return

        self._config.add_piece(piece, count)

        # Add to piece list
        item = QListWidgetItem(piece.name)
        self._piece_list.addItem(item)

        # Store piece widget for reference
        self._piece_widgets[piece.name] = PieceWidget(
            piece_name=piece.name,
            shape=piece.shape,
        )

        # Update UI
        self._update_piece_count()
        self._update_area_display()

        # Emit signal
        self.config_changed.emit(self._config)

    def _remove_piece_from_config(self, piece_name: str) -> None:
        """Remove a piece from the configuration and UI.

        Args:
            piece_name: Name of piece to remove
        """
        if self._config is None:
            return

        # Get the piece object
        piece = self._config.get_piece_by_name(piece_name)
        if piece is None:
            return

        self._config.remove_piece(piece)

        # Remove from piece list
        for i in range(self._piece_list.count()):
            item = self._piece_list.item(i)
            if item.text() == piece_name:
                self._piece_list.takeItem(i)
                break

        # Remove piece widget reference
        self._piece_widgets.pop(piece_name, None)

        # Clear selection if this piece was selected
        if self._selected_piece_name == piece_name:
            self._selected_piece_name = None

        # Update UI
        self._update_piece_count()
        self._update_area_display()

        # Emit signal
        self.config_changed.emit(self._config)

    def _update_ui_from_config(self) -> None:
        """Update UI elements from the current configuration."""
        if self._config is None:
            return

        # Update board dimensions
        self._width_spin.setCurrentText(str(self._config.board_width))
        self._height_spin.setCurrentText(str(self._config.board_height))
        self._board_view.width = self._config.board_width
        self._board_view.height = self._config.board_height

        # Set blocked cells
        self._board_view.set_blocked_cells(self._config.blocked_cells)

        # Update piece list
        self._piece_list.clear()
        self._piece_widgets.clear()

        for piece in self._config.pieces:
            item = QListWidgetItem(piece.name)
            self._piece_list.addItem(item)
            self._piece_widgets[piece.name] = PieceWidget(
                piece_name=piece.name,
                shape=piece.shape,
            )

        # Update displays
        self._update_piece_count()
        self._update_area_display()

    def _update_piece_count(self) -> None:
        """Update the piece count display."""
        if self._config:
            # Count total pieces (with counts)
            count = sum(self._config.pieces.values())
            self._piece_count_label.setText(format_piece_count(count))

    def _update_area_display(self) -> None:
        """Update the area comparison display."""
        if self._config:
            piece_area = self._config.get_total_piece_area()
            board_area = self._config.get_board_area()
            self._area_label.setText(format_area_comparison(piece_area, board_area))

    def _get_current_config(self) -> PuzzleConfiguration:
        """Get the current configuration from UI state.

        Returns:
            Current PuzzleConfiguration
        """
        width = int(self._width_spin.currentText())
        height = int(self._height_spin.currentText())

        # Build pieces dict from current configuration
        pieces_dict: dict[PuzzlePiece, int] = {}
        if self._config:
            pieces_dict = self._config.pieces.copy()

        blocked_cells = self._board_view.blocked_cells

        config = PuzzleConfiguration(
            name="Current Puzzle",
            board_width=width,
            board_height=height,
            pieces=pieces_dict,
            blocked_cells=blocked_cells,
        )

        return config

    # Event handlers

    def _on_board_dimension_changed(self, _value: str) -> None:
        """Handle board dimension changes."""
        width = int(self._width_spin.currentText())
        height = int(self._height_spin.currentText())

        self._board_view.width = width
        self._board_view.height = height

        self._update_area_display()
        self.statusBar().showMessage(f"Board size: {width}×{height}")

    def _on_board_cell_toggled(self, row: int, col: int, filled: bool) -> None:
        """Handle board cell toggle events."""
        self.statusBar().showMessage(
            f"Cell ({row}, {col}) {'filled' if filled else 'cleared'}"
        )

    def _on_piece_selected(self, item: QListWidgetItem) -> None:
        """Handle piece selection in the list."""
        piece_name = item.text()
        self._selected_piece_name = piece_name

        # Update piece widget selection state
        for name, widget in self._piece_widgets.items():
            widget.is_selected = name == piece_name

        # Show piece in editor
        if self._config:
            piece = self._config.get_piece_by_name(piece_name)
            if piece:
                self._piece_name_label.setText(f"<b>{piece.name}</b>")
                self._piece_editor.setVisible(True)
                self._piece_editor.piece_name = piece.name
                self._piece_editor.shape = piece.shape
                self._piece_editor.is_editable = True

        self.statusBar().showMessage(f"Selected piece: {piece_name}")

    def _on_piece_shape_changed(self, shape: set[tuple[int, int]]) -> None:
        """Handle piece shape changes from the editor."""
        if self._config and self._selected_piece_name:
            piece = self._config.get_piece_by_name(self._selected_piece_name)
            if piece:
                # Update the piece in config with new shape
                new_piece = PuzzlePiece(
                    name=piece.name,
                    shape=shape,
                )
                # Preserve the count
                count = self._config.pieces.get(piece, 1)
                self._config.update_piece(new_piece, count)
                self._update_area_display()
                self.config_changed.emit(self._config)

    def _on_piece_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle piece double-click for renaming."""
        piece_name = item.text()
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Piece",
            "Enter new piece name:",
            QLineEdit.EchoMode.Normal,
            piece_name,
        )

        if ok and new_name and new_name != piece_name:
            # Get the piece and create a new one with updated name
            if self._config:
                piece = self._config.get_piece_by_name(piece_name)
                if piece:
                    # Preserve count
                    count = self._config.pieces.get(piece, 1)
                    new_piece = PuzzlePiece(
                        name=new_name,
                        shape=piece.shape,
                    )
                    # Remove old piece and add new one
                    self._config.remove_piece(piece)
                    self._config.add_piece(new_piece, count)

                    # Update UI
                    item.setText(new_name)
                    self._piece_widgets[new_name] = self._piece_widgets.pop(piece_name)
                    self._piece_widgets[new_name].piece_name = new_name
                    self.statusBar().showMessage(f"Piece renamed to: {new_name}")
                    self.config_changed.emit(self._config)

    def _on_add_piece(self) -> None:
        """Handle add piece button click."""
        piece = self._create_piece()
        self._add_piece_to_config(piece)
        self.statusBar().showMessage(f"Added piece: {piece.name}")

    def _on_delete_piece(self) -> None:
        """Handle delete piece button click."""
        current_item = self._piece_list.currentItem()
        if current_item:
            piece_name = current_item.text()
            reply = QMessageBox.question(
                self,
                "Delete Piece",
                f"Delete piece '{piece_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._remove_piece_from_config(piece_name)
                self.statusBar().showMessage(f"Deleted piece: {piece_name}")

    def _on_clear_board(self) -> None:
        """Handle clear board button click."""
        reply = QMessageBox.question(
            self,
            "Clear Board",
            "Clear all filled cells? (Blocked cells will be preserved)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._board_view.clear(keep_blocked=True)
            self.statusBar().showMessage("Board cleared")

    def _on_set_blocked_cells(self) -> None:
        """Handle set blocked cells button click."""
        QMessageBox.information(
            self,
            "Set Blocked Cells",
            "Right-click on cells in the board editor to mark them as blocked.\n\n"
            "Blocked cells appear as gray and cannot be filled with pieces.",
        )

    def _on_new_puzzle(self) -> None:
        """Handle new puzzle action."""
        reply = QMessageBox.question(
            self,
            "New Puzzle",
            "Create a new puzzle? All current configuration will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._create_initial_config()
            self._update_ui_from_config()
            self.statusBar().showMessage("New puzzle created")

    def _on_save_puzzle(self) -> None:
        """Handle save puzzle action."""
        QMessageBox.information(
            self,
            "Save Puzzle",
            "Save functionality will be implemented in User Story 3.",
        )

    def _on_load_puzzle(self) -> None:
        """Handle load puzzle action."""
        QMessageBox.information(
            self,
            "Load Puzzle",
            "Load functionality will be implemented in User Story 3.",
        )

    def _on_export_puzzle(self) -> None:
        """Handle export puzzle action."""
        QMessageBox.information(
            self,
            "Export Puzzle",
            "Export functionality will be implemented in User Story 3.",
        )

    def _on_import_puzzle(self) -> None:
        """Handle import puzzle action."""
        QMessageBox.information(
            self,
            "Import Puzzle",
            "Import functionality will be implemented in User Story 3.",
        )

    def _on_clear_all(self) -> None:
        """Handle clear all action."""
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Clear all pieces and board configuration?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self._config:
                self._config.clear_pieces()
            self._board_view.clear(keep_blocked=False)
            self._piece_list.clear()
            self._piece_widgets.clear()
            self._selected_piece_name = None
            self._update_piece_count()
            self._update_area_display()
            self.statusBar().showMessage("All cleared")

    def _on_solve(self) -> None:
        """Handle solve action."""
        if self._is_solving:
            return

        config = self._get_current_config()

        # Validate
        errors = config.validate()
        if errors:
            QMessageBox.warning(
                self,
                "Cannot Solve",
                "Please fix the following issues:\n\n"
                + "\n".join(f"• {e}" for e in errors),
            )
            return

        self._is_solving = True
        self.statusBar().showMessage("Solving...")
        self.solve_requested.emit(config)

    def _on_about(self) -> None:
        """Handle about action."""
        QMessageBox.about(
            self,
            "About Polyomino Puzzle Solver",
            "<h3>Polyomino Puzzle Solver</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A GUI application for solving polyomino puzzles using "
            "backtracking algorithm with real-time visualization.</p>"
            "<p>Created with PySide6 (Qt6)</p>",
        )

    def set_solving_complete(self) -> None:
        """Called when solving is complete to reset state."""
        self._is_solving = False
        self.statusBar().showMessage("Solving complete")
