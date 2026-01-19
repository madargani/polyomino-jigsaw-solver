"""GameBoard class for representing the puzzle board."""

from __future__ import annotations

from src.models.piece import PuzzlePiece


class GameBoard:
    """Represents the rectangular grid area where pieces must be placed.

    Attributes:
        width: Number of columns in the board
        height: Number of rows in the board
        cells: Grid cells mapping (row, col) -> piece_id or None
        blocked_cells: Set of initially filled (blocked) cell positions
    """

    def __init__(
        self,
        width: int,
        height: int,
        blocked_cells: set[tuple[int, int]] | None = None,
    ) -> None:
        """Initialize a game board with specified dimensions.

        Args:
            width: Number of columns (1-50)
            height: Number of rows (1-50)
            blocked_cells: Set of initially filled (blocked) cell positions

        Raises:
            ValueError: If dimensions are out of valid range
            ValueError: If blocked_cells contain out-of-bounds positions
        """
        if not (1 <= width <= 50):
            raise ValueError("Width must be between 1 and 50")
        if not (1 <= height <= 50):
            raise ValueError("Height must be between 1 and 50")

        self._width = width
        self._height = height
        self._cells: dict[tuple[int, int], int | None] = {
            (row, col): None for row in range(height) for col in range(width)
        }

        # Validate and set blocked cells
        self._blocked_cells: set[tuple[int, int]] = set()
        if blocked_cells:
            for cell in blocked_cells:
                row, col = cell
                if not (0 <= row < height and 0 <= col < width):
                    raise ValueError(
                        f"Blocked cell {cell} is out of board bounds ({width}x{height})"
                    )
                self._blocked_cells.add(cell)
                # Mark blocked cells as occupied in the cells dict (use -1 as special marker)
                self._cells[(row, col)] = -1

    @property
    def width(self) -> int:
        """Get the board width."""
        return self._width

    @property
    def height(self) -> int:
        """Get the board height."""
        return self._height

    @property
    def total_area(self) -> int:
        """Get total number of cells."""
        return self._width * self._height

    @property
    def available_area(self) -> int:
        """Get number of cells available for piece placement (excluding blocked cells)."""
        return self._width * self._height - len(self._blocked_cells)

    @property
    def blocked_cells(self) -> set[tuple[int, int]]:
        """Get the set of blocked cell positions."""
        return self._blocked_cells.copy()

    @property
    def filled_area(self) -> int:
        """Get number of occupied cells."""
        return sum(1 for cell in self._cells.values() if cell is not None)

    @property
    def empty_area(self) -> int:
        """Get number of empty cells."""
        return sum(1 for cell in self._cells.values() if cell is None)

    def can_place_piece(self, piece: PuzzlePiece, position: tuple[int, int]) -> bool:
        """Check if a piece can be placed at the specified position.

        Args:
            piece: The puzzle piece to place
            position: (row, col) position to place piece origin

        Returns:
            True if piece fits without overlapping, going out of bounds, or hitting blocked cells
        """
        piece_shape = piece.canonical_shape
        for row_offset, col_offset in piece_shape:
            row = position[0] + row_offset
            col = position[1] + col_offset

            # Check bounds
            if not (0 <= row < self._height and 0 <= col < self._width):
                return False

            # Check if cell is blocked (initially filled)
            if (row, col) in self._blocked_cells:
                return False

            # Check if cell is already occupied by a piece
            cell_content = self._cells.get((row, col))
            if cell_content is not None and cell_content != -1:
                return False

        return True

    def place_piece(
        self,
        piece: PuzzlePiece,
        position: tuple[int, int],
    ) -> bool:
        """Place a piece at the specified position.

        Args:
            piece: The puzzle piece to place
            position: (row, col) position to place piece origin

        Returns:
            True if piece was placed successfully

        Raises:
            ValueError: If piece cannot be placed at position
        """
        piece_shape = piece.canonical_shape
        if not self.can_place_piece(piece, position):
            raise ValueError(
                f"Cannot place piece at position {position} with shape {piece_shape}"
            )

        for row_offset, col_offset in piece_shape:
            row = position[0] + row_offset
            col = position[1] + col_offset
            # Store piece identifier based on shape hash
            self._cells[(row, col)] = hash(frozenset(piece_shape))

        return True

    def remove_piece(
        self,
        piece: PuzzlePiece,
        position: tuple[int, int],
    ) -> bool:
        """Remove a piece from the board.

        Args:
            piece: The puzzle piece to remove
            position: (row, col) position where piece is placed

        Returns:
            True if piece was removed successfully

        Raises:
            ValueError: If piece is not found at position
        """
        piece_shape = piece.canonical_shape
        # Verify piece exists at position
        piece_hash = hash(frozenset(piece_shape))
        for row_offset, col_offset in piece_shape:
            row = position[0] + row_offset
            col = position[1] + col_offset
            if self._cells.get((row, col)) != piece_hash:
                raise ValueError(f"Piece not found at position {position}")

        # Remove the piece
        for row_offset, col_offset in piece_shape:
            row = position[0] + row_offset
            col = position[1] + col_offset
            self._cells[(row, col)] = None

        return True

    def get_occupied_cells(self) -> set[tuple[int, int]]:
        """Get set of all occupied cell positions.

        Returns:
            Set of (row, col) tuples with pieces placed
        """
        return {pos for pos, piece_id in self._cells.items() if piece_id is not None}

    def get_empty_cells(self) -> set[tuple[int, int]]:
        """Get set of all empty cell positions.

        Returns:
            Set of (row, col) tuples without pieces
        """
        return {pos for pos, piece_id in self._cells.items() if piece_id is None}

    def is_full(self) -> bool:
        """Check if board is completely filled.

        Returns:
            True if all cells are occupied
        """
        return all(cell is not None for cell in self._cells.values())

    def is_empty(self) -> bool:
        """Check if the board is completely empty.

        Returns:
            True if no pieces are placed (blocked cells are ignored)
        """
        # Check if any non-blocked cells are occupied
        return all(cell is None or cell == -1 for cell in self._cells.values())

    def is_blocked(self, position: tuple[int, int]) -> bool:
        """Check if a cell is blocked (initially filled).

        Args:
            position: (row, col) position to query

        Returns:
            True if cell is blocked
        """
        return position in self._blocked_cells

    def get_blocked_cells(self) -> set[tuple[int, int]]:
        """Get set of all blocked cell positions.

        Returns:
            Set of (row, col) tuples that are blocked
        """
        return self._blocked_cells.copy()

    def get_piece_at(self, position: tuple[int, int]) -> int | None:
        """Get the piece ID at the specified position.

        Args:
            position: (row, col) position to query

        Returns:
            Piece ID (hash) if cell is occupied, None otherwise
        """
        return self._cells.get(position)

    def clear(self) -> None:
        """Clear all pieces from the board."""
        for pos in self._cells:
            self._cells[pos] = None

    def copy(self) -> GameBoard:
        """Create a deep copy of the board.

        Returns:
            New GameBoard with identical state (including blocked cells)
        """
        new_board = GameBoard(self._width, self._height, self._blocked_cells.copy())
        new_board._cells = self._cells.copy()
        return new_board

    def __eq__(self, other: object) -> bool:
        """Check equality with another board."""
        if not isinstance(other, GameBoard):
            return NotImplemented
        return (
            self._width == other._width
            and self._height == other._height
            and self._cells == other._cells
            and self._blocked_cells == other._blocked_cells
        )

    def __repr__(self) -> str:
        """Get string representation."""
        return f"GameBoard(width={self._width}, height={self._height})"
