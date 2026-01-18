# Data Model: Polyomino Puzzle Solver

**Feature**: Polyomino Puzzle Solver
**Date**: January 14, 2026

## Table of Contents

1. [Entity Overview](#entity-overview)
2. [Core Entities](#core-entities)
3. [Piece Dictionary Pattern](#piece-dictionary-pattern)
4. [Entity Relationships](#entity-relationships)
5. [Validation Rules](#validation-rules)
6. [State Management](#state-management)

---

## Entity Overview

| Entity                  | Description                                                      | Module                    | Key Attributes                         |
| ----------------------- | ---------------------------------------------------------------- | ------------------------- | -------------------------------------- |
| **PuzzlePiece**         | Represents a connected shape made of square grid cells           | `models/piece.py`         | shape                            |
| **GameBoard**           | Represents the rectangular grid area where pieces must be placed | `models/board.py`         | width, height, cells, blocked_cells    |
| **PuzzleState**         | Represents the current state of the solving process              | `models/puzzle_state.py`  | board, placed_pieces, remaining_pieces |
| **PuzzleConfiguration** | Represents a complete puzzle definition                          | `models/puzzle_config.py` | board_dimensions, pieces               |

---

## Core Entities

### PuzzlePiece

**Purpose**: Represents a single polyomino piece with its shape. Color is generated dynamically during visualization and not stored with the piece. Pieces are identified by their shape hash for dictionary storage.

**Location**: `src/models/piece.py`

#### Attributes

| Attribute                  | Type                   | Description                                            | Constraints                                               |
| -------------------------- | ---------------------- | ------------------------------------------------------ | --------------------------------------------------------- |
| `shape`                    | `Set[Tuple[int, int]]` | Set of (row, col) coordinates defining the piece shape | Required, non-empty, coordinates relative to origin (0,0) |
| `area`                     | `int`                  | Number of cells in the piece (calculated)              | Computed from `len(shape)`, ≥ 1                           |
| `precomputed_orientations` | `List['PuzzlePiece']`  | Precomputed unique orientations (8 max)                | Computed on init, includes 4 rotations × 2 mirrors        |

#### Methods

```python
class PuzzlePiece:
    def __init__(self, shape: Set[Tuple[int, int]]) -> None:
        """Initialize a puzzle piece.

        Args:
            shape: Set of (row, col) coordinates defining the piece shape

        Raises:
            ValueError: If shape is empty or not contiguous
        """
        self.shape = shape
        # Precompute all 8 orientations (4 rotations × 2 mirrors) for performance
        self.precomputed_orientations = self._compute_all_orientations()
```

#### Validation Rules

1. **Non-empty shape**: Shape must contain at least one cell
2. **Contiguous**: All cells must be connected (4-directional adjacency)
3. **Origin relative**: Shape should be normalized (min row/col = 0,0)
4. **Unique rotations**: `get_rotations()` must return deduplicated orientations
5. **Precomputed orientations**: Must include up to 8 total orientations (4 rotations × 2 mirrors), deduplicated
6. **Orientation count**: `get_precomputed_orientations()` returns 1-8 unique orientations based on piece symmetry

#### State Transitions

```
[Created Piece]
     │
     ├─ rotate(90) ──► [Rotated Piece] (new instance)
     │
     ├─ rotate(180) ─► [Rotated Piece] (new instance)
     │
     ├─ rotate(270) ─► [Rotated Piece] (new instance)
     │
     └─ flip('horizontal') ─► [Flipped Piece] (new instance)
```

**Note**: All transformation methods return new instances, preserving immutability.

---

### GameBoard

**Purpose**: Represents the rectangular grid area where pieces must be placed without overlap.

**Location**: `src/models/board.py`

#### Attributes

| Attribute        | Type                                   | Description                                       | Constraints                                       |
| ---------------- | -------------------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| `width`          | `int`                                  | Number of columns in the board                    | Required, 1 ≤ width ≤ 50                          |
| `height`         | `int`                                  | Number of rows in the board                       | Required, 1 ≤ height ≤ 50                         |
| `cells`          | `Dict[Tuple[int, int], Optional[str]]` | Grid cells mapping (row,col) → piece_id           | Required, initialized to None                     |
| `blocked_cells`  | `Set[Tuple[int, int]]`                 | Set of initially filled (blocked) cell positions  | Required, immutable, cannot be occupied by pieces |
| `total_area`     | `int`                                  | Total number of cells (calculated)                | Computed from width × height                      |
| `available_area` | `int`                                  | Number of cells available for pieces (calculated) | Computed from total_area - len(blocked_cells)     |

#### Methods

````python
class GameBoard:
    def __init__(
        self,
        width: int,
        height: int,
        blocked_cells: Optional[Set[Tuple[int, int]]] = None
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

    def can_place_piece(self, piece: PuzzlePiece, position: Tuple[int, int]) -> bool:
        """Check if a piece can be placed at the specified position.

        Args:
            piece: The puzzle piece to place
            position: (row, col) position to place piece origin

        Returns:
            True if piece fits without overlapping, going out of bounds, or hitting blocked cells
        """

    def place_piece(self, piece: PuzzlePiece, position: Tuple[int, int]) -> bool:
        """Place a piece at the specified position.

        Args:
            piece: The puzzle piece to place
            position: (row, col) position to place piece origin

        Returns:
            True if piece was placed successfully

        Raises:
            ValueError: If piece cannot be placed at position
        """

    def remove_piece(self, piece: PuzzlePiece, position: Tuple[int, int]) -> None:
        """Remove a piece from the board.

        Args:
            piece: The puzzle piece to remove
            position: (row, col) position where piece is placed

        Raises:
            ValueError: If piece is not found at position
        """

    def get_occupied_cells(self) -> Set[Tuple[int, int]]:
        """Get set of all occupied cell positions.

        Returns:
            Set of (row, col) tuples with pieces placed
        """

    def get_empty_cells(self) -> Set[Tuple[int, int]]:
        """Get set of all empty cell positions.

        Returns:
            Set of (row, col) tuples without pieces
        """

    def is_full(self) -> bool:
        """Check if board is completely filled.

        Returns:
            True if all cells are occupied
        """

    def is_empty(self) -> bool:
        """Check if board is completely empty.

        Returns:
            True if no pieces are placed
        """

    def is_blocked(self, position: Tuple[int, int]) -> bool:
        """Check if a cell is blocked (initially filled).

        Args:
            position: (row, col) position to query

        Returns:
            True if cell is blocked
        """

    def get_blocked_cells(self) -> Set[Tuple[int, int]]:
        """Get set of all blocked cell positions.

        Returns:
            Set of (row, col) tuples that are blocked
        """

    def get_piece_at(self, position: Tuple[int, int]) -> Optional[str]:
        """Get the piece ID at the specified position.

        Args:
            position: (row, col) position to query

        Returns:
            Piece ID if cell is occupied, None otherwise
        """

    def clear(self) -> None:
        """Clear all pieces from the board."""

    def copy(self) -> 'GameBoard':
        """Create a deep copy of the board.

        Returns:
            New GameBoard with identical state
        """

    @property
    def filled_area(self) -> int:
        """Get number of occupied cells."""

    @property
    def empty_area(self) -> int:
        """Get number of empty cells."""

    @property
    def available_area(self) -> int:
        """Get number of cells available for piece placement (excluding blocked cells)."""
    ```

#### Validation Rules

1. **Dimension limits**: 1 ≤ width ≤ 50, 1 ≤ height ≤ 50
2. **Blocked cells in bounds**: All blocked_cells positions must be within board boundaries
3. **In-bounds placement**: All piece cells must be within board boundaries
4. **No overlap**: Piece cells cannot occupy already-filled cells or blocked cells
5. **Valid piece ID**: Piece must exist before placement/removal
6. **Blocked cells immutable**: blocked_cells cannot be modified after board creation

#### State Transitions

````

[Empty Board]
│
├─ place_piece(piece, pos) ──► [Piece Added]
│ │
│ ├─ place_piece(piece2, pos2) ──► [Multiple Pieces]
│ │
│ └─ remove_piece(piece, pos) ───► [Empty Board]
│
└─ clear() ──────────────────► [Empty Board]

````

---

## Piece Dictionary Pattern

### Why Use a Dictionary for Pieces?

Many polyomino puzzles require multiple copies of the same piece shape. For example:
- A puzzle might need 4 L-tetrominoes, 2 T-tetrominoes, and 1 I-tetromino
- Storing each piece separately would require repeating the same shape data
- A dictionary `Dict[PuzzlePiece, int]` elegantly represents this: `{piece_shape: count}`

### Benefits

1. **Memory Efficiency**: Each unique piece shape is stored once, regardless of count
2. **Clear Semantics**: `{L_piece: 3}` clearly means "three L-tetrominoes"
3. **Easy Updates**: Increment/decrement counts when adding/removing pieces
4. **Natural JSON Format**: `{"name": "L-tetromino", "shape": [...], "count": 3}` is intuitive
5. **Solver Integration**: Tracking remaining pieces becomes simple count management

### Example: Multiple Copies of Same Piece

```python
# Create unique piece definitions
l_piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
t_piece = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2), (1, 1)})

# A puzzle with 3 L's and 2 T's
config = PuzzleConfiguration(
    name="My Puzzle",
    board_width=6,
    board_height=6,
    pieces={
        l_piece: 3,  # Three L-tetrominoes
        t_piece: 2   # Two T-tetrominoes
    }
)

# Total piece count: 5
print(f"Total pieces: {sum(config.pieces.values())}")

# Piece area: 3*4 + 2*4 = 20 cells
print(f"Total area: {config.get_piece_area()}")
````

### Solver Integration

The solver receives the piece dictionary and manages counts during solving:

```python
# Solver receives: {L_piece: 3, T_piece: 2}
state = PuzzleState(board, pieces_dict)

# Place an L-piece
state.place_piece(L_piece, (0, 0))  # L_piece count decrements to 2

# Backtrack: remove and restore count
removed = state.remove_piece((0, 0))  # L_piece count increments back to 3
```

---

### PuzzleState

**Purpose**: Represents the current state of the solving process, including board configuration, placed pieces, and backtrack history.

**Location**: `src/models/puzzle_state.py`

#### Attributes

| Attribute           | Type                                        | Description                            | Constraints                     |
| ------------------- | ------------------------------------------- | -------------------------------------- | ------------------------------- |
| `board`             | `GameBoard`                                 | Current board configuration            | Required                        |
| `placed_pieces`     | `List[Tuple[PuzzlePiece, Tuple[int, int]]]` | List of (piece, position) tuples       | Required, ordered by placement  |
| `remaining_pieces`  | `Dict[PuzzlePiece, int]`                    | Dictionary of piece to remaining count | Required, piece → count mapping |
| `backtrack_history` | `List[Dict[str, Any]]`                      | History of solver operations           | Required, append-only           |

#### Methods

```python
class PuzzleState:
    def __init__(
        self,
        board: GameBoard,
        pieces: Dict[PuzzlePiece, int]
    ) -> None:
        """Initialize puzzle state with board and pieces.

        Args:
            board: The game board
            pieces: Dictionary mapping piece to count (how many of that piece remain)
        """
        self.board = board
        self.remaining_pieces = pieces.copy()  # Copy to avoid mutation
        self.placed_pieces = []
        self.backtrack_history = []

    def place_piece(
        self,
        piece: PuzzlePiece,
        position: Tuple[int, int]
    ) -> bool:
        """Place a piece and record in state.

        Args:
            piece: The puzzle piece to place
            position: (row, col) position to place piece

        Returns:
            True if piece was placed successfully

        Raises:
            ValueError: If piece cannot be placed or no more of that piece remain
        """
        # Check if we have any of this piece remaining
        if self.remaining_pieces.get(piece, 0) <= 0:
            raise ValueError(f"No more pieces of this shape remaining")

        # Check if piece can be placed on board
        if not self.board.can_place_piece(piece, position):
            return False

        # Place the piece
        self.board.place_piece(piece, position)
        self.placed_pieces.append((piece, position))

        # Decrement remaining count
        self.remaining_pieces[piece] = self.remaining_pieces.get(piece, 0) - 1
        if self.remaining_pieces[piece] == 0:
            del self.remaining_pieces[piece]

        return True

    def remove_piece(self, position: Tuple[int, int]) -> Optional[PuzzlePiece]:
        """Remove a piece from the board (backtrack).

        Args:
            position: (row, col) position to remove piece from

        Returns:
            The piece that was removed, or None if no piece at position
        """
        # Find the piece at this position
        for i, (piece, pos) in enumerate(self.placed_pieces):
            if pos == position:
                # Remove from board
                self.board.remove_piece(piece, position)
                # Remove from placed pieces
                self.placed_pieces.pop(i)
                # Increment remaining count
                self.remaining_pieces[piece] = self.remaining_pieces.get(piece, 0) + 1
                return piece
        return None

    def get_total_remaining_pieces(self) -> int:
        """Get total count of all remaining pieces.

        Returns:
            Sum of all piece counts in remaining_pieces
        """
        return sum(self.remaining_pieces.values())

    def record_operation(
        self,
        operation: str,
        piece_id: str,
        position: Tuple[int, int],
        orientation: Optional[PuzzlePiece] = None
    ) -> None:
        """Record a solver operation for history/visualization.

        Args:
            operation: 'place' or 'remove'
            piece_id: ID of the piece
            position: (row, col) position
            orientation: Piece orientation (for placement)
        """

    def get_last_operation(self) -> Optional[Dict[str, Any]]:
        """Get the most recent operation.

        Returns:
            Operation dict or None if no operations recorded
        """

    def is_solved(self) -> bool:
        """Check if puzzle is solved.

        Returns:
            True if all pieces are placed and board is full
        """

    def can_proceed(self) -> bool:
        """Check if solving can proceed.

        Returns:
            True if there are pieces left to place
        """

    def copy(self) -> 'PuzzleState':
        """Create a deep copy of the puzzle state.

        Returns:
            New PuzzleState with identical state
        """

    def get_statistics(self) -> Dict[str, Any]:
        """Get solver statistics.

        Returns:
            Dict with 'placements', 'removals', 'backtracks', etc.
        """
```

#### Validation Rules

1. **Piece exists**: Piece must be in available_pieces before placement
2. **Valid index**: current_index must track actual progress
3. **History consistency**: Backtrack history must match placed pieces
4. **State consistency**: board must reflect all placed pieces

#### State Transitions

```
[Initial State]
     │
     ├─ place_piece(piece, pos) ──► [Piece Placed]
     │                               │
     │                               ├─ place_piece(piece2, pos2) ──► [More Pieces]
     │                               │
     │                               └─ remove_piece(pos) ───────────► [Backtrack]
     │                                                            │
     │                                                            └─ place_piece(...) ──► [Retry]
     │
     └─ [is_solved() = True] ────────► [Solved State]
```

---

### PuzzleConfiguration

**Purpose**: Represents a complete puzzle definition containing board dimensions and the set of polyomino pieces with counts.

**Location**: `src/models/puzzle_config.py`

#### Attributes

| Attribute       | Type                     | Description                               | Constraints                     |
| --------------- | ------------------------ | ----------------------------------------- | ------------------------------- |
| `name`          | `str`                    | User-defined puzzle name                  | Required, unique within puzzles |
| `board_width`   | `int`                    | Board width in cells                      | Required, 1 ≤ width ≤ 50        |
| `board_height`  | `int`                    | Board height in cells                     | Required, 1 ≤ height ≤ 50       |
| `blocked_cells` | `Set[Tuple[int, int]]`   | Initially filled (blocked) cell positions | Optional, defaults to empty set |
| `pieces`        | `Dict[PuzzlePiece, int]` | Dictionary of piece to count              | Required, non-empty, count ≥ 1  |
| `created_at`    | `datetime`               | Timestamp when configuration was created  | Required                        |
| `modified_at`   | `datetime`               | Timestamp of last modification            | Required                        |

#### Methods

```python
class PuzzleConfiguration:
    def __init__(
        self,
        name: str,
        board_width: int,
        board_height: int,
        pieces: Dict[PuzzlePiece, int],
        blocked_cells: Optional[Set[Tuple[int, int]]] = None
    ) -> None:
        """Initialize a puzzle configuration.

        Args:
            name: User-defined puzzle name
            board_width: Board width in cells (1-50)
            board_height: Board height in cells (1-50)
            pieces: Dictionary mapping piece to count (how many of that piece)
            blocked_cells: Set of initially filled (blocked) cell positions

        Raises:
            ValueError: If constraints are violated
        """

    def validate(self) -> List[str]:
        """Validate the configuration.

        Returns:
            List of validation errors (empty if valid)
        """

    def add_piece(self, piece: PuzzlePiece, count: int = 1) -> None:
        """Add a piece to the configuration.

        Args:
            piece: Puzzle piece to add
            count: Number of copies to add (default: 1)

        Raises:
            ValueError: If piece is invalid
        """

    def remove_piece(self, piece: PuzzlePiece, count: int = 1) -> None:
        """Remove a piece from the configuration.

        Args:
            piece: Piece to remove
            count: Number of copies to remove (default: 1)

        Raises:
            ValueError: If piece not found or count exceeds available
        """

    def get_all_pieces(self) -> List[PuzzlePiece]:
        """Get list of all pieces (expanding counts).

        Returns:
            List of pieces with each piece repeated according to its count
        """
        all_pieces = []
        for piece, count in self.pieces.items():
            all_pieces.extend([piece] * count)
        return all_pieces

    def get_piece_counts(self) -> Dict[str, int]:
        """Get mapping of piece shapes to their counts.

        Returns:
            Dictionary of piece shape hash -> count
        """
        return {str(piece.shape): count for piece, count in self.pieces.items()}

    def get_board(self) -> GameBoard:
        """Create a GameBoard from configuration.

        Returns:
            New GameBoard instance with blocked_cells configured
        """
        return GameBoard(
            width=self.board_width,
            height=self.board_height,
            blocked_cells=self.blocked_cells
        )

    def get_piece_area(self) -> int:
        """Get total area of all pieces (accounting for counts).

        Returns:
            Sum of all piece areas multiplied by their counts
        """
        total = 0
        for piece, count in self.pieces.items():
            total += len(piece.shape) * count
        return total

    def get_board_area(self) -> int:
        """Get total board area.

        Returns:
            board_width × board_height
        """

    def is_solvable_area(self) -> bool:
        """Check if piece area matches available board area.

        Returns:
            True if total piece area equals available board area (total_area - blocked_cells)
        """

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization.

        Returns:
            Dictionary representation including blocked_cells and piece counts
        """
        return {
            'name': self.name,
            'board_width': self.board_width,
            'board_height': self.board_height,
            'blocked_cells': list(self.blocked_cells),
            'pieces': [
                {'shape': list(piece.shape), 'count': count}
                for piece, count in self.pieces.items()
            ],
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PuzzleConfiguration':
        """Create configuration from dictionary.

        Args:
            data: Dictionary representation including piece counts

        Returns:
            New PuzzleConfiguration instance

        Raises:
            ValueError: If data is invalid
        """
        # Parse blocked_cells (handle missing field for backward compatibility)
        blocked_cells = set()
        if 'blocked_cells' in data:
            blocked_cells = set(tuple(cell) for cell in data['blocked_cells'])

        # Parse pieces with counts
        pieces_dict: Dict[PuzzlePiece, int] = {}
        for p in data['pieces']:
            shape = set(tuple(coord) for coord in p['shape'])
            piece = PuzzlePiece(shape=shape)
            count = p.get('count', 1)  # Default to 1 for backward compatibility
            pieces_dict[piece] = count

        return cls(
            name=data['name'],
            board_width=data['board_width'],
            board_height=data['board_height'],
            pieces=pieces_dict,
            blocked_cells=blocked_cells
        )

    def copy(self) -> 'PuzzleConfiguration':
        """Create a deep copy of the configuration.

        Returns:
            New PuzzleConfiguration with identical state
        """
```

#### Validation Rules

1. **Non-empty pieces**: At least one piece must be defined with count ≥ 1
2. **Valid dimensions**: Board dimensions must be 1-50
3. **Blocked cells in bounds**: All blocked_cells positions must be within board boundaries
4. **Positive counts**: All piece counts must be ≥ 1
5. **Unique piece shapes**: All piece shapes within a configuration must be unique (no duplicate shapes)
6. **Area check**: Total piece area must equal available board area (total_area - blocked_cells) (optional warning, not error)
7. **Unique name**: Puzzle name must be unique within saved puzzles

#### State Transitions

```
[New Configuration]
     │
     ├─ add_piece(piece) ──► [Piece Added]
     │                       │
     │                       ├─ add_piece(piece2) ──► [More Pieces]
     │                       │
     │                       └─ remove_piece(id) ────► [Piece Removed]
     │
     └─ [save/load] ──────────────────────────────────► [Persisted Configuration]
```

---

## Entity Relationships

### Relationship Diagram

```
┌─────────────────────┐
│ PuzzleConfiguration │
│ - name              │◄────────────────┐
│ - board_width       │                 │
│ - board_height      │                 │
│ - pieces{}          │                 │
└─────────────────────┘                 │
         │ 1                           │
         │ has                         │ 1..*
         │                             │
         ▼                             │
┌─────────────────────┐   1..*         │    count
│    PuzzlePiece       │◄───────────────┼───────────► int
│ - shape             │
└─────────────────────┘
         │
         │ 0..*
         │ placed in
         │
         ▼
┌─────────────────────┐
│      GameBoard      │◄────────────────┐
│ - width             │                 │
│ - height            │                 │
│ - cells{}           │                 │
└─────────────────────┘                 │
         │                             │
         │ tracked by                  │ 1
         │                             │
         ▼                             │
┌─────────────────────┐                 │
│    PuzzleState      │                 │
│ - board             │                 │
│ - placed_pieces[]   │                 │
│ - remaining_pieces{}│                 │
└─────────────────────┘                 │
                                           │
         1..*                             │
         │ records                        │
         │                                │
         └────────────────────────────────┘
```

### Relationship Descriptions

| Relationship                          | Type          | Description                                                                               |
| ------------------------------------- | ------------- | ----------------------------------------------------------------------------------------- |
| **PuzzleConfiguration → PuzzlePiece** | 1..\* → count | Configuration contains unique pieces with counts (e.g., 3 L-tetrominoes, 2 I-tetrominoes) |
| **PuzzlePiece → GameBoard**           | 0..\*         | Pieces can be placed on board (many orientations)                                         |
| **GameBoard → PuzzleState**           | 1             | Board is tracked by exactly one state during solving                                      |
| **PuzzleState → Remaining Pieces**    | 1..\* → count | State tracks how many of each piece remain to be placed                                   |

### Cascading Behaviors

- **Deleting PuzzleConfiguration**: Does not delete pieces (pieces may be reused in other configurations)
- **Modifying Piece Count**: Changing count in PuzzleConfiguration.pieces affects total piece area calculation
- **Clearing Board**: Does not affect PuzzleConfiguration (can rebuild board)
- **Copying PuzzleState**: Creates deep copy of board, placed pieces, and remaining_pieces dictionary
- **Adding Same Piece Twice**: Increments count in pieces dictionary (e.g., {L-piece: 2} → {L-piece: 3})

---

## Validation Rules

### Cross-Entity Validation

1. **Piece Area vs Available Board Area**
   - **Rule**: Total piece area should equal available board area (board_area - blocked_cells) for solvability
   - **Enforcement**: Warning in PuzzleConfiguration.validate(), not error
   - **Rationale**: User may want to define unsolvable puzzles for testing

2. **Blocked Cells vs Board Boundaries**
   - **Rule**: All blocked cell positions must be within board dimensions
   - **Enforcement**: Error in GameBoard.**init**() and PuzzleConfiguration.validate()
   - **Rationale**: Prevents invalid state and ensures consistent behavior

3. **Piece Placement vs Blocked Cells**
   - **Rule**: Pieces cannot be placed on blocked cells
   - **Enforcement**: Error in GameBoard.can_place_piece() and GameBoard.place_piece()
   - **Rationale**: Blocked cells are permanently unavailable for piece placement

4. **Piece Count Validation**
   - **Rule**: All piece counts must be ≥ 1
   - **Enforcement**: Error in PuzzleConfiguration.**init**() and add_piece()
   - **Rationale**: Negative or zero counts are invalid

5. **Unique Piece Shapes**
   - **Rule**: All piece shapes within a configuration must be unique
   - **Enforcement**: Error in PuzzleConfiguration.add_piece()
   - **Rationale**: Duplicate shapes would cause dictionary key conflicts

6. **Contiguous Piece Shapes**
   - **Rule**: All cells in a piece must be 4-connected
   - **Enforcement**: Error in PuzzlePiece.**init**()
   - **Rationale**: By definition, polyominoes are connected shapes

### Validation Flow

```python
# When creating a new puzzle with piece counts
l_piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
config = PuzzleConfiguration(
    name="My Puzzle",
    width=4,
    height=4,
    pieces={l_piece: 4}  # 4 L-tetrominoes
)
errors = config.validate()

if errors:
    # Display errors to user
    # e.g., "Piece area (16) does not match board area (16)"
    pass
else:
    # Proceed with solver
    board = config.get_board()
    state = PuzzleState(board, config.pieces)  # Pass dictionary with counts
```

### Error Hierarchy

1. **Critical Errors** (prevent operation):
   - Invalid dimensions
   - Empty piece shape
   - Non-contiguous piece
   - Duplicate piece shapes
   - Invalid piece counts (≤ 0)
   - Out-of-bounds placement

2. **Warnings** (allow operation but inform user):
   - Piece area ≠ board area
   - Very large puzzle (may take long to solve)
   - Many pieces (may be difficult to solve)

---

## State Management

### Immutable vs Mutable

**Immutable** (return new instances):

- `PuzzlePiece.rotate()`, `PuzzlePiece.flip()`
- `GameBoard.copy()`, `PuzzleState.copy()`, `PuzzleConfiguration.copy()`

**Mutable** (modify in place):

- `GameBoard.place_piece()`, `GameBoard.remove_piece()`, `GameBoard.clear()`
- `PuzzleState.place_piece()`, `PuzzleState.remove_piece()` (modifies remaining_pieces dict)
- `PuzzleConfiguration.add_piece()`, `PuzzleConfiguration.remove_piece()` (modifies pieces dict)

### Thread Safety Considerations

- **Read operations**: Thread-safe (no modification)
- **Write operations**: Not thread-safe, require external synchronization
- **Solver pattern**: Solver runs in separate thread, state is modified there
- **GUI updates**: Use Qt signals to communicate state changes to GUI thread

### Persistence Strategy

**JSON Serialization Format**:

```json
{
  "name": "My Puzzle",
  "board_width": 5,
  "board_height": 5,
  "blocked_cells": [
    [0, 0],
    [0, 1],
    [2, 3]
  ],
  "pieces": [
    {
      "shape": [
        [0, 0],
        [1, 0],
        [1, 1],
        [1, 2]
      ],
      "count": 3
    },
    {
      "shape": [
        [0, 0],
        [0, 1],
        [0, 2],
        [0, 3]
      ],
      "count": 2
    }
  ],
  "created_at": "2026-01-14T12:00:00Z",
  "modified_at": "2026-01-14T12:30:00Z"
}
```

**Deserialization**: Reconstruct objects from dictionaries using `from_dict()` methods

**File Locations**:

- Saved puzzles: `~/.polyomino-puzzles/saved/{name}.json`
- Exported puzzles: User-specified location

---

## Usage Examples

### Creating a Simple Puzzle

```python
from models.piece import PuzzlePiece
from models.board import GameBoard
from models.puzzle_config import PuzzleConfiguration

# Define pieces (color is generated dynamically during visualization)
# Each piece is identified by its shape for dictionary storage
l_piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
t_piece = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2), (1, 1)})
i_piece = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2), (0, 3)})

# Create configuration with piece counts (dictionary format)
config = PuzzleConfiguration(
    name="Simple 4x4",
    board_width=4,
    board_height=4,
    pieces={
        l_piece: 2,  # 2 L-tetrominoes
        t_piece: 1,  # 1 T-tetromino
        i_piece: 1   # 1 I-tetromino
    }
)

# Validate
errors = config.validate()
if errors:
    print("Validation errors:", errors)
else:
    print("Configuration is valid!")
    print(f"Total pieces: {sum(config.pieces.values())}")  # Output: Total pieces: 4
```

### Using the Solver

```python
from logic.solver import BacktrackingSolver
from models.puzzle_state import PuzzleState

# Create board and state
board = config.get_board()
state = PuzzleState(board, config.pieces)  # Pass the dictionary directly

# Run solver
solver = BacktrackingSolver(callback_delay=0.1)
result = solver.solve(config.pieces, board)

if result:
    print("Puzzle solved!")
    print(f"Placements: {len(state.placed_pieces)}")
    print(f"Remaining pieces: {state.get_total_remaining_pieces()}")
else:
    print("No solution found")
```

### Working with Piece Orientations

```python
# Get all unique rotations
rotations = piece1.get_rotations()
print(f"Piece has {len(rotations)} unique rotations")

# Get all orientations (rotations + flips)
orientations = piece1.get_all_orientations()
print(f"Piece has {len(orientations)} unique orientations")

# Rotate a piece
rotated = piece1.rotate(90)
print(f"Rotated shape: {rotated.shape}")

# Flip a piece
flipped = piece1.flip('horizontal')
print(f"Flipped shape: {flipped.shape}")
```
