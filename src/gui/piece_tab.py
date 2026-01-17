"""Piece tab component for the puzzle editor.

This module contains the PieceTab class which provides the UI for creating
and editing polyomino pieces through a grid-based drawing interface.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen, QResizeEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.models.piece import PuzzlePiece


class PieceGridWidget(QWidget):
    """Grid widget for drawing and editing piece shapes.

    This widget provides a grid-based drawing interface where users can
    create polyomino pieces by clicking and dragging to add cells.

    Attributes:
        grid_width: Width of the drawing grid
        grid_height: Height of the drawing grid
        filled_cells: Set of filled cell positions (row, col)
    """

    # Constants
    MIN_CELL_SIZE = 15
    MAX_CELL_SIZE = 50
    DEFAULT_CELL_SIZE = 30
    FILL_COLOR = QColor(0, 123, 255)  # Blue for filled cells
    GRID_COLOR = QColor(180, 180, 180)  # Medium gray for grid lines

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the piece grid widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._grid_width = 10
        self._grid_height = 10
        self._filled_cells: set[tuple[int, int]] = set()
        self._cell_size = self.DEFAULT_CELL_SIZE
        self._is_filling = True  # True = add cells, False = remove cells

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    @property
    def grid_width(self) -> int:
        """Get the grid width."""
        return self._grid_width

    @grid_width.setter
    def grid_width(self, value: int) -> None:
        """Set the grid width.

        Args:
            value: New width (1-50)
        """
        self._grid_width = max(1, min(50, value))
        self._trim_filled_cells()
        self.updateGeometry()
        self.update()

    @property
    def grid_height(self) -> int:
        """Get the grid height."""
        return self._grid_height

    @grid_height.setter
    def grid_height(self, value: int) -> None:
        """Set the grid height.

        Args:
            value: New height (1-50)
        """
        self._grid_height = max(1, min(50, value))
        self._trim_filled_cells()
        self.updateGeometry()
        self.update()

    @property
    def filled_cells(self) -> set[tuple[int, int]]:
        """Get the set of filled cell positions."""
        return self._filled_cells.copy()

    @filled_cells.setter
    def filled_cells(self, cells: set[tuple[int, int]]) -> None:
        """Set the filled cells and update display.

        Args:
            cells: Set of (row, col) positions to mark as filled
        """
        self._filled_cells = cells.copy()
        self._trim_filled_cells()
        self.update()

    def _trim_filled_cells(self) -> None:
        """Remove filled cells that are outside the grid bounds."""
        self._filled_cells = {
            (r, c)
            for r, c in self._filled_cells
            if 0 <= r < self._grid_height and 0 <= c < self._grid_width
        }

    def set_dimensions(self, width: int, height: int) -> None:
        """Set grid dimensions.

        Args:
            width: New width (1-50)
            height: New height (1-50)
        """
        self._grid_width = max(1, min(50, width))
        self._grid_height = max(1, min(50, height))
        self._trim_filled_cells()
        self.updateGeometry()
        self.update()

    def clear(self) -> None:
        """Clear all filled cells."""
        self._filled_cells.clear()
        self.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle widget resize to auto-fit cell size."""
        self._calculate_cell_size()
        super().resizeEvent(event)

    def _calculate_cell_size(self) -> None:
        """Calculate optimal cell size based on available space."""
        available_width = self.width() - 10
        available_height = self.height() - 10

        if self._grid_width > 0 and self._grid_height > 0:
            cell_width = available_width // self._grid_width
            cell_height = available_height // self._grid_height
            self._cell_size = max(
                self.MIN_CELL_SIZE, min(cell_width, cell_height, self.MAX_CELL_SIZE)
            )

    def sizeHint(self) -> QSize:
        """Return the preferred size hint."""
        width = self._grid_width * self._cell_size + 10
        height = self._grid_height * self._cell_size + 10
        return QSize(width, height)

    def minimumSizeHint(self) -> QSize:
        """Return the minimum size hint."""
        width = self._grid_width * self.MIN_CELL_SIZE + 10
        height = self._grid_height * self.MIN_CELL_SIZE + 10
        return QSize(width, height)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate grid position (centered)
        grid_width = self._grid_width * self._cell_size
        grid_height = self._grid_height * self._cell_size
        offset_x = (self.width() - grid_width) // 2
        offset_y = (self.height() - grid_height) // 2

        # Draw cells
        for row in range(self._grid_height):
            for col in range(self._grid_width):
                x = offset_x + col * self._cell_size
                y = offset_y + row * self._cell_size

                # Determine cell color
                if (row, col) in self._filled_cells:
                    color = self.FILL_COLOR
                else:
                    color = QColor(255, 255, 255)

                painter.fillRect(x, y, self._cell_size, self._cell_size, color)

                # Draw grid lines
                pen = QPen(self.GRID_COLOR)
                pen.setWidth(1)
                painter.setPen(pen)
                painter.drawRect(x, y, self._cell_size, self._cell_size)

        # Draw row/column labels if cells are large enough
        if self._cell_size >= 20:
            font = painter.font()
            font.setPointSize(max(7, min(10, self._cell_size // 3)))
            painter.setFont(font)
            painter.setPen(QColor(100, 100, 100))

            # Column labels (top)
            for col in range(self._grid_width):
                x = offset_x + col * self._cell_size + self._cell_size // 2
                y = offset_y - 5
                label = str(col)
                metrics = painter.fontMetrics()
                text_width = metrics.horizontalAdvance(label)
                painter.drawText(int(x - text_width // 2), int(y), label)

            # Row labels (left)
            for row in range(self._grid_height):
                x = offset_x - 5
                y = offset_y + row * self._cell_size + self._cell_size // 2
                label = str(row)
                metrics = painter.fontMetrics()
                text_height = metrics.height()
                painter.drawText(
                    int(x - metrics.horizontalAdvance(label)),
                    int(y + text_height // 3),
                    label,
                )

    def _get_cell_at_position(
        self, pos_x: int, pos_y: int
    ) -> tuple[int, int] | None:
        """Get the cell coordinates at the given position.

        Args:
            pos_x: X coordinate in widget space
            pos_y: Y coordinate in widget space

        Returns:
            (row, col) tuple or None if position is outside the grid
        """
        grid_width = self._grid_width * self._cell_size
        grid_height = self._grid_height * self._cell_size
        offset_x = (self.width() - grid_width) // 2
        offset_y = (self.height() - grid_height) // 2

        # Check if position is within grid bounds
        if pos_x < offset_x or pos_x >= offset_x + grid_width:
            return None
        if pos_y < offset_y or pos_y >= offset_y + grid_height:
            return None

        col = (pos_x - offset_x) // self._cell_size
        row = (pos_y - offset_y) // self._cell_size

        if 0 <= row < self._grid_height and 0 <= col < self._grid_width:
            return (row, col)
        return None

    def mousePressEvent(self, event) -> None:
        """Handle mouse press for toggling cells."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_filling = True
            self._toggle_cell_at_position(event.pos())
        elif event.button() == Qt.MouseButton.RightButton:
            self._is_filling = False
            self._toggle_cell_at_position(event.pos())

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse drag for painting cells."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._is_filling = True
            self._toggle_cell_at_position(event.pos())
        elif event.buttons() & Qt.MouseButton.RightButton:
            self._is_filling = False
            self._toggle_cell_at_position(event.pos())

    def _toggle_cell_at_position(self, pos) -> None:
        """Toggle cell state at the given position.

        Args:
            pos: QPoint position
        """
        cell = self._get_cell_at_position(pos.x(), pos.y())
        if cell is not None:
            if self._is_filling:
                self._filled_cells.add(cell)
            else:
                self._filled_cells.discard(cell)
            self.update()


class PieceTab(QWidget):
    """Tab widget for piece creation and editing.

    This tab provides a piece list for managing multiple pieces and a grid
    editor for drawing piece shapes.

    Signals:
        piece_selected: Emitted when a piece is selected from the list
        piece_added: Emitted when a new piece is added
        piece_deleted: Emitted when a piece is deleted
        piece_modified: Emitted when a piece shape is modified
    """

    # Signals
    piece_selected = Signal(PuzzlePiece)
    piece_added = Signal(PuzzlePiece)
    piece_deleted = Signal(PuzzlePiece)
    piece_modified = Signal(PuzzlePiece)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the piece tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._pieces: list[PuzzlePiece] = []
        self._selected_piece: PuzzlePiece | None = None
        self._piece_counter = 0

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        # Main layout with pieces list on left and editor on right
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Left side: Piece list
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        pieces_label = QLabel("Pieces:")
        pieces_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_panel.addWidget(pieces_label)

        # Piece list widget
        self._piece_list = QListWidget()
        self._piece_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._piece_list.setFixedWidth(150)
        self._piece_list.itemSelectionChanged.connect(self._on_piece_selection_changed)
        left_panel.addWidget(self._piece_list)

        # Piece count label
        self._piece_count_label = QLabel("Pieces: 0")
        left_panel.addWidget(self._piece_count_label)

        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)

        self._add_button = QPushButton("Add Piece")
        self._add_button.clicked.connect(self._on_add_piece)
        button_layout.addWidget(self._add_button)

        self._delete_button = QPushButton("Delete Piece")
        self._delete_button.clicked.connect(self._on_delete_piece)
        button_layout.addWidget(self._delete_button)

        self._clear_button = QPushButton("Clear Shape")
        self._clear_button.clicked.connect(self._on_clear_shape)
        button_layout.addWidget(self._clear_button)

        left_panel.addLayout(button_layout)

        # Add spacer
        left_panel.addStretch()

        main_layout.addLayout(left_panel)

        # Right side: Grid editor
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        # Instructions
        instructions = QLabel(
            "Click and drag to draw piece shape.\nRight-click to erase cells."
        )
        instructions.setStyleSheet("color: #666; font-style: italic;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(instructions)

        # Grid dimensions controls
        grid_size_layout = QHBoxLayout()
        grid_size_layout.setSpacing(10)

        width_label = QLabel("Grid Width:")
        self._width_spinner = QSpinBox()
        self._width_spinner.setRange(1, 20)
        self._width_spinner.setValue(10)
        self._width_spinner.setFixedWidth(80)
        self._width_spinner.valueChanged.connect(self._on_grid_size_changed)

        height_label = QLabel("Height:")
        self._height_spinner = QSpinBox()
        self._height_spinner.setRange(1, 20)
        self._height_spinner.setValue(10)
        self._height_spinner.setFixedWidth(80)
        self._height_spinner.valueChanged.connect(self._on_grid_size_changed)

        grid_size_layout.addWidget(width_label)
        grid_size_layout.addWidget(self._width_spinner)
        grid_size_layout.addWidget(height_label)
        grid_size_layout.addWidget(self._height_spinner)
        grid_size_layout.addStretch()

        right_panel.addLayout(grid_size_layout)

        # Piece grid
        self._grid_widget = PieceGridWidget()
        self._grid_widget.setMinimumSize(300, 300)
        right_panel.addWidget(self._grid_widget)

        # Shape info
        self._shape_info_label = QLabel("Cells: 0")
        self._shape_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self._shape_info_label)

        # Set row stretch for the grid area to expand
        right_panel.setStretch(2, 1)

        main_layout.addLayout(right_panel)

        # Set stretch ratio
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 3)

    def _on_piece_selection_changed(self) -> None:
        """Handle piece selection changes."""
        selected_items = self._piece_list.selectedItems()
        if selected_items:
            index = self._piece_list.row(selected_items[0])
            if 0 <= index < len(self._pieces):
                self._selected_piece = self._pieces[index]
                # Load the piece shape into the grid
                shape = self._selected_piece.shape
                self._grid_widget.filled_cells = shape.copy()
                self._update_shape_info()
        else:
            self._selected_piece = None
            self._grid_widget.clear()
            self._update_shape_info()

        self.piece_selected.emit(self._selected_piece)

    def _on_add_piece(self) -> None:
        """Handle adding a new piece."""
        self._piece_counter += 1
        piece_name = f"Piece {self._piece_counter}"

        # Create new piece from current grid
        shape = self._grid_widget.filled_cells
        if not shape:
            # Create empty piece - user will draw it
            shape = {(0, 0)}

        piece = PuzzlePiece(name=piece_name, shape=shape)
        self._pieces.append(piece)

        # Add to list
        item = QListWidgetItem(piece_name)
        item.setData(Qt.ItemDataRole.UserRole, piece)
        self._piece_list.addItem(item)
        self._piece_list.setCurrentRow(len(self._pieces) - 1)

        self._piece_count_label.setText(f"Pieces: {len(self._pieces)}")
        self.piece_added.emit(piece)

    def _on_delete_piece(self) -> None:
        """Handle deleting the selected piece."""
        if self._selected_piece is None:
            return

        piece_to_delete = self._selected_piece
        index = self._pieces.index(piece_to_delete)

        # Remove from list
        self._pieces.pop(index)
        self._piece_list.takeItem(index)

        # Clear selection and grid
        self._selected_piece = None
        self._grid_widget.clear()

        # Select next piece or clear
        if self._pieces:
            new_index = min(index, len(self._pieces) - 1)
            self._piece_list.setCurrentRow(new_index)
        else:
            self._piece_count_label.setText("Pieces: 0")

        self.piece_deleted.emit(piece_to_delete)

    def _on_clear_shape(self) -> None:
        """Handle clearing the current shape."""
        self._grid_widget.clear()
        self._update_shape_info()

        # Update selected piece if any
        if self._selected_piece:
            # Create updated piece
            new_piece = PuzzlePiece(name=self._selected_piece.name, shape=set())
            index = self._pieces.index(self._selected_piece)
            self._pieces[index] = new_piece
            self._selected_piece = new_piece
            self.piece_modified.emit(new_piece)

    def _on_grid_size_changed(self) -> None:
        """Handle grid size changes."""
        width = self._width_spinner.value()
        height = self._height_spinner.value()
        self._grid_widget.set_dimensions(width, height)

    def _update_shape_info(self) -> None:
        """Update the shape information label."""
        cell_count = len(self._grid_widget.filled_cells)
        self._shape_info_label.setText(f"Cells: {cell_count}")

    @property
    def pieces(self) -> list[PuzzlePiece]:
        """Get the list of all pieces."""
        return self._pieces.copy()

    @property
    def selected_piece(self) -> PuzzlePiece | None:
        """Get the currently selected piece."""
        return self._selected_piece

    def get_current_shape(self) -> set[tuple[int, int]]:
        """Get the current shape from the grid.

        Returns:
            Set of (row, col) coordinates representing the current shape
        """
        return self._grid_widget.filled_cells

    def save_current_shape_to_piece(self) -> None:
        """Save the current grid shape to the selected piece."""
        if self._selected_piece is not None:
            shape = self._grid_widget.filled_cells
            index = self._pieces.index(self._selected_piece)
            new_piece = PuzzlePiece(name=self._selected_piece.name, shape=shape)
            self._pieces[index] = new_piece
            self._selected_piece = new_piece
            self.piece_modified.emit(new_piece)

    def add_piece(self, piece: PuzzlePiece) -> None:
        """Add a piece to the list.

        Args:
            piece: The piece to add
        """
        self._pieces.append(piece)

        # Update counter if this is an auto-named piece
        if piece.name.startswith("Piece "):
            try:
                num = int(piece.name.split()[-1])
                self._piece_counter = max(self._piece_counter, num)
            except ValueError:
                pass

        # Add to list
        item = QListWidgetItem(piece.name)
        item.setData(Qt.ItemDataRole.UserRole, piece)
        self._piece_list.addItem(item)
        self._piece_count_label.setText(f"Pieces: {len(self._pieces)}")

    def clear_all(self) -> None:
        """Clear all pieces and reset the UI."""
        self._pieces.clear()
        self._selected_piece = None
        self._piece_list.clear()
        self._grid_widget.clear()
        self._piece_count_label.setText("Pieces: 0")
        self._update_shape_info()
