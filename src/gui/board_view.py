"""BoardView widget for editing the puzzle board grid."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QResizeEvent
from PySide6.QtWidgets import QWidget


class BoardView(QWidget):
    """Grid-based board editor widget.

    Signals:
        cell_clicked: Emitted when a cell is clicked (row, col)
        cell_toggled: Emitted when a cell is toggled via drawing (row, col, filled)
        board_resized: Emitted when board dimensions change (width, height)
    """

    cell_clicked = Signal(int, int)
    cell_toggled = Signal(int, int, bool)
    board_resized = Signal(int, int)

    def __init__(
        self,
        width: int = 5,
        height: int = 5,
        cell_size: int = 40,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the board view widget.

        Args:
            width: Initial board width in cells
            height: Initial board height in cells
            cell_size: Size of each cell in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self._width = width
        self._height = height
        self._cell_size = cell_size
        self._filled_cells: set[tuple[int, int]] = set()
        self._blocked_cells: set[tuple[int, int]] = set()
        self._selected_cell: tuple[int, int] | None = None
        self._is_drawing = False
        self._draw_mode = False  # True = fill, False = clear

        self._setup_style()
        self.setMinimumSize(200, 200)

    def _setup_style(self) -> None:
        """Configure widget styling."""
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    @property
    def width(self) -> int:
        """Get the board width in cells."""
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        """Set the board width in cells."""
        if 1 <= value <= 50 and value != self._width:
            self._width = value
            self._filled_cells = {(r, c) for r, c in self._filled_cells if c < value}
            self._blocked_cells = {(r, c) for r, c in self._blocked_cells if c < value}
            self.update()
            self.board_resized.emit(self._width, self._height)

    @property
    def height(self) -> int:
        """Get the board height in cells."""
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        """Set the board height in cells."""
        if 1 <= value <= 50 and value != self._height:
            self._height = value
            self._filled_cells = {(r, c) for r, c in self._filled_cells if r < value}
            self._blocked_cells = {(r, c) for r, c in self._blocked_cells if r < value}
            self.update()
            self.board_resized.emit(self._width, self._height)

    @property
    def cell_size(self) -> int:
        """Get the cell size in pixels."""
        return self._cell_size

    @cell_size.setter
    def cell_size(self, value: int) -> None:
        """Set the cell size in pixels."""
        if value >= 20 and value != self._cell_size:
            self._cell_size = value
            self.update()

    def get_cell_at_position(self, pos: QPoint) -> tuple[int, int] | None:
        """Get cell coordinates at the given position.

        Args:
            pos: QPoint in widget coordinates

        Returns:
            (row, col) tuple or None if position is outside the board
        """
        x = pos.x()
        y = pos.y()

        col = x // self._cell_size
        row = y // self._cell_size

        if 0 <= row < self._height and 0 <= col < self._width:
            return (row, col)
        return None

    def is_cell_filled(self, row: int, col: int) -> bool:
        """Check if a cell is filled."""
        return (row, col) in self._filled_cells

    def is_cell_blocked(self, row: int, col: int) -> bool:
        """Check if a cell is blocked."""
        return (row, col) in self._blocked_cells

    def set_cell_filled(self, row: int, col: int, filled: bool) -> None:
        """Set the fill state of a cell."""
        if 0 <= row < self._height and 0 <= col < self._width:
            if filled:
                self._filled_cells.add((row, col))
            else:
                self._filled_cells.discard((row, col))
            self.update()

    def set_cell_blocked(self, row: int, col: int, blocked: bool) -> None:
        """Set the blocked state of a cell."""
        if 0 <= row < self._height and 0 <= col < self._width:
            if blocked:
                self._blocked_cells.add((row, col))
            else:
                self._blocked_cells.discard((row, col))
            self.update()

    def toggle_cell(self, row: int, col: int) -> None:
        """Toggle the fill state of a cell."""
        if 0 <= row < self._height and 0 <= col < self._width:
            if (row, col) in self._filled_cells:
                self._filled_cells.discard((row, col))
            else:
                self._filled_cells.add((row, col))
            self.cell_toggled.emit(row, col, (row, col) in self._filled_cells)
            self.update()

    def clear_all(self) -> None:
        """Clear all filled cells (preserve blocked cells)."""
        self._filled_cells.clear()
        self.update()

    def set_blocked_cells(self, cells: set[tuple[int, int]]) -> None:
        """Set the blocked cells."""
        self._blocked_cells = cells.copy()
        self.update()

    @property
    def blocked_cells(self) -> set[tuple[int, int]]:
        """Get the blocked cells."""
        return self._blocked_cells.copy()

    def clear(self, keep_blocked: bool = True) -> None:
        """Clear all filled cells.

        Args:
            keep_blocked: If True, preserve blocked cells
        """
        if keep_blocked:
            self._filled_cells.clear()
        else:
            self._filled_cells.clear()
            self._blocked_cells.clear()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            cell = self.get_cell_at_position(event.pos())
            if cell is not None:
                self._is_drawing = True
                row, col = cell
                self._draw_mode = (row, col) not in self._filled_cells
                self.toggle_cell(row, col)
                self.cell_clicked.emit(row, col)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events for drag-drawing."""
        if self._is_drawing:
            cell = self.get_cell_at_position(event.pos())
            if cell is not None:
                row, col = cell
                is_filled = (row, col) in self._filled_cells
                if is_filled != self._draw_mode:
                    self.toggle_cell(row, col)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events."""
        self._is_drawing = False

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leaving the widget."""
        self._is_drawing = False

    def paintEvent(self, event: QEvent) -> None:
        """Paint the board grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor("#FFFFFF"))

        # Draw grid cells
        for row in range(self._height):
            for col in range(self._width):
                x = col * self._cell_size
                y = row * self._cell_size
                rect = QRect(x + 1, y + 1, self._cell_size - 2, self._cell_size - 2)

                # Determine cell color
                if (row, col) in self._blocked_cells:
                    color = QColor("#CCCCCC")  # Gray for blocked
                elif (row, col) in self._filled_cells:
                    color = QColor("#4A90D9")  # Blue for filled
                else:
                    color = QColor("#FFFFFF")  # White for empty

                painter.fillRect(rect, color)

                # Draw cell border
                pen = QPen(QColor("#999999"))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.drawRect(rect)

        # Draw grid lines for better visibility
        self._draw_grid_lines(painter)

        # Draw selection highlight
        if self._selected_cell is not None:
            self._draw_selection(painter)

    def _draw_grid_lines(self, painter: QPainter) -> None:
        """Draw vertical and horizontal grid lines."""
        pen = QPen(QColor("#DDDDDD"))
        pen.setWidth(1)
        painter.setPen(pen)

        # Vertical lines
        for col in range(1, self._width):
            x = col * self._cell_size
            painter.drawLine(x, 0, x, self._height * self._cell_size)

        # Horizontal lines
        for row in range(1, self._height):
            y = row * self._cell_size
            painter.drawLine(0, y, self._width * self._cell_size, y)

    def _draw_selection(self, painter: QPainter) -> None:
        """Draw selection highlight around selected cell."""
        row, col = self._selected_cell
        x = col * self._cell_size
        y = row * self._cell_size

        pen = QPen(QColor("#FF6B35"))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawRect(x + 2, y + 2, self._cell_size - 4, self._cell_size - 4)

    def sizeHint(self) -> QSize:
        """Return the recommended size for this widget."""
        return QSize(self._width * self._cell_size, self._height * self._cell_size)

    def minimumSizeHint(self) -> QSize:
        """Return the minimum size hint for this widget."""
        return QSize(
            max(200, self._width * self._cell_size),
            max(200, self._height * self._cell_size),
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize events."""
        super().resizeEvent(event)
        # Calculate optimal cell size based on new size
        new_width = event.size().width() // max(1, self._width)
        new_height = event.size().height() // max(1, self._height)
        self._cell_size = min(new_width, new_height, 60)
