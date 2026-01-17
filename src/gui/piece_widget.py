"""PieceWidget component for displaying and editing polyomino pieces."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QEvent, QPoint, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget


def generate_piece_color(piece_name: str) -> str:
    """Generate a consistent color for a piece based on its name.

    Args:
        piece_name: The unique name of the piece

    Returns:
        CSS color string (hsl format for vibrant colors)
    """
    import hashlib

    hash_val = int(hashlib.md5(piece_name.encode()).hexdigest(), 16)
    hue = hash_val % 360
    return f"hsl({hue}, 70%, 50%)"


class PieceWidget(QFrame):
    """Widget for displaying and editing a single polyomino piece shape.

    Signals:
        shape_changed: Emitted when the piece shape is modified
        clicked: Emitted when the piece is clicked
    """

    shape_changed = Signal(set[tuple[int, int]])
    clicked = Signal()

    def __init__(
        self,
        piece_name: str = "",
        shape: Optional[set[tuple[int, int]]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the piece widget.

        Args:
            piece_name: Unique identifier for the piece (used for color generation)
            shape: Initial shape (set of (row, col) tuples)
            parent: Parent widget
        """
        super().__init__(parent)
        self._piece_name = piece_name
        self._shape = shape.copy() if shape else {(0, 0)}
        self._cell_size = 20
        self._is_selected = False
        self._is_editable = True

        self._setup_ui()
        self._update_minimum_size()

    def _setup_ui(self) -> None:
        """Set up UI properties."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.setStyleSheet(
            "PieceWidget { "
            "border-color: #999; "
            "background-color: #f5f5f5; "
            "}"
            "PieceWidget:selected { "
            "border-color: #4A90D9; "
            "background-color: #e8f0fe; "
            "}"
        )
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def _update_minimum_size(self) -> None:
        """Update minimum size based on shape."""
        if not self._shape:
            self.setMinimumSize(60, 60)
            return

        max_row = max(r for r, _ in self._shape)
        max_col = max(c for _, c in self._shape)

        width = (max_col + 1) * self._cell_size + self.lineWidth() * 2 + 10
        height = (max_row + 1) * self._cell_size + self.lineWidth() * 2 + 10

        self.setMinimumSize(width, height)

    @property
    def piece_name(self) -> str:
        """Get the piece name."""
        return self._piece_name

    @piece_name.setter
    def piece_name(self, value: str) -> None:
        """Set the piece name."""
        self._piece_name = value

    @property
    def shape(self) -> set[tuple[int, int]]:
        """Get the piece shape."""
        return self._shape.copy()

    @shape.setter
    def shape(self, value: set[tuple[int, int]]) -> None:
        """Set the piece shape."""
        self._shape = value.copy()
        self._update_minimum_size()
        self.update()

    @property
    def color(self) -> str:
        """Get the piece color (generated from name)."""
        return generate_piece_color(self._piece_name)

    @property
    def is_selected(self) -> bool:
        """Check if the piece is selected."""
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool) -> None:
        """Set the selection state."""
        self._is_selected = value
        if value:
            self.setStyleSheet(
                "PieceWidget { "
                "border-color: #4A90D9; "
                "border-width: 3px; "
                "background-color: #e8f0fe; "
                "}"
            )
        else:
            self.setStyleSheet(
                "PieceWidget { "
                "border-color: #999; "
                "border-width: 2px; "
                "background-color: #f5f5f5; "
                "}"
            )
        self.update()

    @property
    def is_editable(self) -> bool:
        """Check if the piece is editable."""
        return self._is_editable

    @is_editable.setter
    def is_editable(self, value: bool) -> None:
        """Set the editable state."""
        self._is_editable = value
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if value else Qt.CursorShape.ArrowCursor
        )

    @property
    def cell_size(self) -> int:
        """Get the cell size in pixels."""
        return self._cell_size

    @cell_size.setter
    def cell_size(self, value: int) -> None:
        """Set the cell size in pixels."""
        if 10 <= value <= 50:
            self._cell_size = value
            self._update_minimum_size()
            self.update()

    @property
    def area(self) -> int:
        """Get the number of cells in the piece."""
        return len(self._shape)

    def add_cell(self, row: int, col: int) -> None:
        """Add a cell to the piece shape.

        Args:
            row: Row offset
            col: Column offset
        """
        self._shape.add((row, col))
        self._update_minimum_size()
        self.update()
        self.shape_changed.emit(self._shape)

    def remove_cell(self, row: int, col: int) -> None:
        """Remove a cell from the piece shape.

        Args:
            row: Row offset
            col: Column offset
        """
        self._shape.discard((row, col))
        self._update_minimum_size()
        self.update()
        self.shape_changed.emit(self._shape)

    def toggle_cell(self, row: int, col: int) -> None:
        """Toggle a cell's presence in the shape.

        Args:
            row: Row offset
            col: Column offset
        """
        if (row, col) in self._shape:
            self._shape.discard((row, col))
        else:
            self._shape.add((row, col))
        self._update_minimum_size()
        self.update()
        self.shape_changed.emit(self._shape)

    def clear(self) -> None:
        """Clear the piece shape (keep at least one cell)."""
        if len(self._shape) > 1:
            self._shape = {(0, 0)}
            self._update_minimum_size()
            self.update()
            self.shape_changed.emit(self._shape)

    def get_normalized_shape(self) -> set[tuple[int, int]]:
        """Get the shape normalized to origin (0, 0).

        Returns:
            Normalized shape with min row and col = 0
        """
        if not self._shape:
            return set()

        min_row = min(r for r, _ in self._shape)
        min_col = min(c for _, c in self._shape)

        return {(r - min_row, c - min_col) for r, c in self._shape}

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the piece shape.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor("#f5f5f5"))

        if not self._shape:
            return

        # Normalize shape for display
        normalized = self.get_normalized_shape()
        min_row = min(r for r, _ in normalized)
        min_col = min(c for _, c in normalized)

        # Draw cells
        fill_color = QColor(self.color)
        painter.fillRect

        for row, col in normalized:
            x = (col - min_col) * self._cell_size + self.lineWidth() + 5
            y = (row - min_row) * self._cell_size + self.lineWidth() + 5
            size = self._cell_size

            # Fill cell
            painter.fillRect(x + 1, y + 1, size - 2, size - 2, fill_color)

            # Draw cell border
            pen = QPen(QColor("#333333"))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(x + 1, y + 1, size - 2, size - 2)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            self.is_selected = True

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move.

        Args:
            event: Mouse event
        """
        if self._is_editable and event.buttons() & Qt.MouseButton.LeftButton:
            # Calculate cell position
            cell_col = (event.pos().x() - self.lineWidth() - 5) // self._cell_size
            cell_row = (event.pos().y() - self.lineWidth() - 5) // self._cell_size

            # Normalize to shape origin
            normalized = self.get_normalized_shape()
            if normalized:
                min_row = min(r for r, _ in normalized)
                min_col = min(c for _, c in normalized)
                cell_row += min_row
                cell_col += min_col

            # Toggle cell
            if (cell_row, cell_col) not in self._shape:
                self.add_cell(cell_row, cell_col)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release.

        Args:
            event: Mouse event
        """
        pass

    def enterEvent(self, event: QEvent) -> None:
        """Handle mouse enter."""
        if self._is_editable:
            self.setCursor(Qt.CursorShape.CrossCursor)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leave."""
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if self._is_editable
            else Qt.CursorShape.ArrowCursor
        )

    def sizeHint(self) -> QSize:
        """Return the recommended size for this widget."""
        return self.minimumSizeHint()

    def minimumSizeHint(self) -> QSize:
        """Return the minimum size hint for this widget."""
        if not self._shape:
            return QSize(60, 60)

        normalized = self.get_normalized_shape()
        max_row = max(r for r, _ in normalized)
        max_col = max(c for _, c in normalized)

        width = (max_col + 1) * self._cell_size + self.lineWidth() * 2 + 10
        height = (max_row + 1) * self._cell_size + self.lineWidth() * 2 + 10

        return QSize(max(width, 60), max(height, 60))
