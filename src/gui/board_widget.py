"""BoardWidget class for rendering puzzle board using QPainter.

This module provides a pure QPainter-based rendering component that displays
the puzzle board state. Single responsibility: draw the board based on received
events. Does NOT contain timing or solver logic.
"""

from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class BoardWidget(QWidget):
    """Renders puzzle board state using QPainter.

    Single responsibility: draw the board based on received events.
    Does NOT contain timing or solver logic.
    """

    def __init__(
        self,
        width: int,
        height: int,
        cell_size: int = 30,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize board widget.

        Args:
            width: Number of columns
            height: Number of rows
            cell_size: Pixel size for each cell (default 30px)
            parent: Parent widget
        """
        super().__init__(parent)
        self._width = width
        self._height = height
        self._cell_size = cell_size

        # Calculate required size
        self.setMinimumSize(
            width * cell_size + 2,
            height * cell_size + 2,
        )

        # State for rendering
        self._board: Optional[Any] = None  # board_snapshot from event
        self._current_piece: Optional[Any] = None  # current_piece from event
        self._current_position: Optional[tuple[int, int]] = (
            None  # current_position from event
        )

    def set_cell_size(self, cell_size: int) -> None:
        """Update the cell size and recalculate widget size.

        Args:
            cell_size: New pixel size for each cell
        """
        self._cell_size = cell_size
        self.setMinimumSize(
            self._width * cell_size + 2,
            self._height * cell_size + 2,
        )
        self.updateGeometry()
        self.update()

    def handle_event(self, event: dict[str, Any]) -> None:
        """Update state based on solver event and trigger repaint.

        Args:
            event: Solver event dictionary with keys:
                - board_snapshot: Current board state
                - current_piece: Piece being attempted (optional)
                - current_position: Position being tried (optional)
        """
        self._board = event.get("board_snapshot")
        self._current_piece = event.get("current_piece")
        self._current_position = event.get("current_position")
        self.update()

    def paintEvent(self, event) -> None:
        """Override to render board using QPainter."""
        if self._board is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw each cell
        for row in range(self._height):
            for col in range(self._width):
                rect = QRectF(
                    col * self._cell_size + 1,
                    row * self._cell_size + 1,
                    self._cell_size - 2,
                    self._cell_size - 2,
                )

                # Determine cell state
                if self._board.is_blocked((row, col)):
                    color = QColor("#333333")  # Blocked cells
                else:
                    piece_id = self._board.get_piece_at((row, col))
                    if piece_id is not None:
                        color = self._get_piece_color(piece_id)
                    else:
                        color = QColor("#FFFFFF")  # Empty cells

                # Draw cell background
                painter.fillRect(rect, color)
                painter.setPen(QPen(QColor("#888888"), 1))
                painter.drawRect(rect)

        # Draw current piece being attempted (if any)
        if self._current_piece and self._current_position:
            self._draw_current_piece(painter)

    def _get_piece_color(self, piece_id: int) -> QColor:
        """Get color for a piece based on its ID.

        Args:
            piece_id: The piece identifier (hash)

        Returns:
            QColor for this piece
        """
        # Generate color from piece_id using HSL
        hue = abs(piece_id) % 360
        return QColor.fromHslF(hue / 360, 0.7, 0.6)

    def _draw_current_piece(self, painter: QPainter) -> None:
        """Draw the current piece being attempted (with transparency).

        Args:
            painter: QPainter instance
        """
        if not self._current_piece or not self._current_position:
            return

        row_offset, col_offset = self._current_position
        shape = self._current_piece.canonical_shape

        # Semi-transparent color for "tentative" piece
        color = QColor(255, 0, 0, 128)  # Red with transparency

        for cell_row, cell_col in shape:
            row = row_offset + cell_row
            col = col_offset + cell_col

            if 0 <= row < self._height and 0 <= col < self._width:
                rect = QRectF(
                    col * self._cell_size + 1,
                    row * self._cell_size + 1,
                    self._cell_size - 2,
                    self._cell_size - 2,
                )
                painter.fillRect(rect, color)
                painter.setPen(QPen(QColor("#FF0000"), 2))
                painter.drawRect(rect)
