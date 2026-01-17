# Feature Specification: Polyomino Puzzle Solver

**Feature Branch**: `[001-polyomino-puzzle-solver]`
**Created**: January 14, 2026
**Status**: Draft
**Input**: User description: "Build an app in python that solves a jigsaw puzzle with polyomino pieces. Initially the app will open a GUI where the user can manually input the pieces of the puzzle and the shape of the board. After, when the user presses solve, the app will open another window where it will give a visualization of the program trying to solve the puzzle using a backtracking algorithm."

## Clarifications

### Session 2026-01-16

- Q: When you say "all possible transformations" for puzzle pieces, what specific transformations should be precomputed? This affects both the number of orientations generated and the solving algorithm's approach. → A: Rotations + Mirrors (rotate 0°, 90°, 180°, 270° and mirror each rotation for 8 total orientations)
- Q: How should users define initially filled (blocked) cells on the board? Should this be through manual placement in the editor, importing from files, or both? → A: Both methods (manual placement in grid editor + import from files)

### Session 2026-01-14

- Q: What format should be used for saving/loading puzzle configurations and export/import? → A: JSON (JavaScript Object Notation)
- Q: What should be the maximum allowed board dimensions (width × height in cells) that the application can handle? → A: 50×50 cells
- Q: Should users be able to control the visualization speed during solving, or should it be a fixed delay? → A: User-adjustable speed control (slider or presets)
- Q: Should pieces be distinguished by unique colors in the visualization, or use a single color for all pieces? → A: Unique colors for each piece type
- Q: When the user modifies the puzzle configuration while the solver is running, how should the system respond? → A: Disable edit controls during solving with notification

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define Puzzle Configuration (Priority: P1)

The user launches the application and sees a graphical interface where they can define the puzzle pieces and board shape. They interact with a grid-based editor to draw the shape of each polyomino piece, specify the dimensions of the board where pieces will be placed, and optionally mark certain cells as initially filled (blocked). The user can add multiple pieces of various shapes and sizes to their puzzle configuration and define boards with pre-filled regions.

**Why this priority**: This is the foundational user journey - without the ability to define puzzles, no other functionality can exist. It represents the core value proposition of allowing users to create and solve custom puzzles.

**Independent Test**: Can be tested by launching the application, drawing a simple piece, setting board dimensions, and verifying the configuration persists. Delivers the ability to define puzzle structures without needing solving capabilities.

**Acceptance Scenarios**:

1. **Given** the application is launched, **When** the user switches to the "Pieces" tab, **Then** the piece editor is displayed with full screen height available
2. **Given** the application is launched, **When** the user switches to the "Board" tab, **Then** the board editor is displayed with full screen height available
3. **Given** the user is in the Pieces tab, **When** they click and drag on the grid, **Then** cells are painted following the cursor motion
4. **Given** the user is in either editor tab, **When** they right-click on a cell, **Then** the cell toggles between filled and empty states
5. **Given** the user is in the Board tab, **When** they set the board dimensions (width and height), **Then** the board grid is automatically resized to fit within the visible screen area
6. **Given** the user is in the Board tab, **When** they mark cells as initially filled, **Then** those cells are displayed as blocked and unavailable for piece placement
7. **Given** the user is in the Pieces tab, **When** they draw a shape on the grid, **Then** the shape is visually displayed and stored as a defined piece
8. **Given** multiple pieces have been defined, **When** the user selects a piece from the list, **Then** the piece shape is highlighted in the editor
9. **Given** a piece has been defined, **When** the user deletes it, **Then** the piece is removed from the configuration

---

### User Story 2 - Solve Puzzle Visualization (Priority: P2)

After defining the puzzle configuration, the user clicks the "Solve" button. A new window opens displaying the board and pieces. The application shows a real-time visualization of the backtracking algorithm attempting to place pieces on the board. The user watches as pieces are tried in different positions, backtracking when placements lead to dead ends, until a solution is found or all possibilities are exhausted.

**Why this priority**: This is the primary user-facing outcome - users want to see the algorithm work and understand how the solution is reached. It provides educational value and demonstrates the problem-solving process.

**Independent Test**: Can be tested by defining a simple solvable puzzle (e.g., 2x2 board with two L-shaped tetrominoes), clicking solve, and verifying pieces are placed on the board with visible backtracking behavior when dead ends are encountered.

**Acceptance Scenarios**:

1. **Given** a valid puzzle configuration, **When** the user clicks "Solve", **Then** a new visualization window opens showing the empty board
2. **Given** the visualization window is open, **When** the algorithm attempts a piece placement, **Then** the piece appears on the board in the trial position
3. **Given** a piece placement leads to a dead end, **When** the algorithm backtracks, **Then** the piece is removed and a different placement is tried
4. **Given** the algorithm finds a solution, **When** the board is fully filled, **Then** all pieces are displayed in their final positions and the process stops
5. **Given** no solution exists, **When** all possibilities are exhausted, **Then** the visualization indicates that no solution was found

---

### User Story 3 - Puzzle Management (Priority: P3)

The user can save puzzle configurations for later use and load previously saved puzzles. They can also clear the current configuration to start fresh, export puzzle configurations to share with others, and import configurations received from other users. Board configurations with initially filled cells can be saved, loaded, and shared alongside piece definitions.

**Why this priority**: This enhances usability by allowing users to build a library of puzzles and share interesting configurations. It's valuable but not essential for core functionality.

**Independent Test**: Can be tested by creating a puzzle configuration, saving it, clearing the editor, loading the saved puzzle, and verifying the configuration matches what was saved. Delivers persistence and sharing capabilities.

**Acceptance Scenarios**:

1. **Given** a puzzle configuration is defined, **When** the user saves it with a name, **Then** the configuration is stored and appears in the list of saved puzzles
2. **Given** saved puzzles exist, **When** the user selects and loads one, **Then** the editor displays the loaded configuration exactly as saved (including any initially filled cells)
3. **Given** a puzzle configuration is defined, **When** the user clicks "Clear", **Then** all pieces, board dimensions, and filled cell markings are reset to the default state
4. **Given** a puzzle configuration, **When** the user exports it, **Then** a file is created containing the puzzle data including board configuration with filled cells
5. **Given** a puzzle file, **When** the user imports it, **Then** the editor displays the imported configuration including any initially filled cells

---

### Edge Cases

- What happens when the user defines pieces that have a total area larger than the board area (excluding initially filled cells)?
- What happens when the user defines no pieces or an empty board?
- What happens when pieces have overlapping shapes or invalid geometries?
- How does the system handle puzzles at the maximum limit (50×50 board with many pieces)?
- What happens if the user clicks "Solve" multiple times quickly?
- How does the visualization handle puzzles that take an extremely long time to solve or are computationally intractable?
- What happens when the user closes the visualization window before solving completes?
- When the user attempts to modify the puzzle configuration while the solver is running, edit controls are disabled and a notification is displayed informing the user that editing is locked during solving
- What happens when initially filled cells make the puzzle unsolvable (e.g., isolated regions that cannot accommodate any piece)?
- What happens when the user marks cells as filled that would leave insufficient space for all pieces?
- How does the system handle imported board configurations with conflicting filled cell data?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a graphical interface for defining polyomino piece shapes on a grid
- **FR-001a**: System MUST use a tabbed interface with separate tabs for "Pieces" and "Board" editing to maximize available screen space
- **FR-001b**: System MUST resize piece and board grid displays to fit within the visible screen area without requiring scrolling
- **FR-001c**: System MUST use consistent interaction patterns for both piece editor and board editor:
  - Left-click to add/remove cells
  - Click-and-drag to paint multiple cells
  - Right-click to toggle cell state
- **FR-002**: System MUST allow users to specify board dimensions through the graphical interface, with maximum dimensions of 50×50 cells
- **FR-003**: System MUST support defining multiple polyomino pieces of various shapes and sizes
- **FR-004**: System MUST validate that piece shapes are contiguous and contain at least one grid cell
- **FR-005**: System MUST visualize piece types with clear visual distinction in both editor and visualization windows
- **FR-005a**: System MUST generate unique colors for each piece type dynamically during visualization (pieces do not store color attributes)
- **FR-005b**: System MUST automatically resize grid displays to fit within the visible screen area
- **FR-005c**: Precomputed transformations MUST include rotations at 0°, 90°, 180°, and 270° plus mirrored versions of each rotation (8 total orientations per piece)
- **FR-005d**: System MUST allow users to define board configurations with cells that are initially filled (blocked)
- **FR-005e**: System MUST provide manual controls for placing blocked cells on the board in the grid editor
- **FR-005f**: System MUST support importing board configurations with pre-filled cells from JSON files
- **FR-005g**: Initially filled cells MUST be treated as unavailable for piece placement during solving
- **FR-006**: System MUST provide a "Solve" action that triggers the solving algorithm
- **FR-007**: System MUST open a separate visualization window when solving begins
- **FR-008**: System MUST display the board grid in the visualization window
- **FR-009**: System MUST show real-time placement of pieces as the algorithm attempts solutions
- **FR-010**: System MUST visualize backtracking by removing pieces and trying alternative placements
- **FR-011**: System MUST indicate when a complete solution has been found
- **FR-012**: System MUST indicate when no solution exists after exhaustive search
- **FR-013**: System MUST allow users to interrupt or stop the solving process at any time
- **FR-014**: System MUST disable edit controls while the solver is running and display a notification to the user
- **FR-015**: System MUST allow users to adjust visualization speed during solving through slider or preset options
- **FR-016**: System MUST prevent duplicate piece placements in the same position during a single solution attempt
- **FR-017**: System MUST support rotating pieces at 90°, 180°, and 270° orientations during solving
- **FR-018**: System MUST support flipping (mirroring) pieces during solving to create additional orientation variations
- **FR-019**: System MUST save and load puzzle configurations using JSON format
- **FR-020**: System MUST export and import puzzle configurations using JSON format

### Key Entities

- **Polyomino Piece**: Represents a connected shape made of square grid cells, characterized by its shape (pattern of cells) and its precomputed transformation set (8 orientations). Pieces do not include color or ID attributes—these are generated dynamically by the visualization system.
- **Board**: Represents the rectangular grid area where pieces must be placed without overlap to solve the puzzle, characterized by its width, height, initially filled (blocked) cells, and dynamic cell occupancy state during solving
- **Puzzle Configuration**: Represents a complete puzzle definition containing the board dimensions and the set of polyomino pieces that must be placed
- **Solution State**: Represents the current state of the solving process, including the current board configuration, pieces placed, placement order, and backtracking history

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can define a complete puzzle configuration (board + pieces) in under 3 minutes
- **SC-002**: The solver visualization shows piece placements with default delay of 100ms between placements for puzzles with up to 20 pieces, with user-adjustable speed control
- **SC-003**: 95% of users successfully define and solve their first puzzle within 5 minutes of launching the application
- **SC-004**: The application maintains a minimum of 30 frames per second during visualization for puzzles with up to 50 total grid cells
- **SC-005**: 80% of users can correctly identify when backtracking occurs in the visualization (verified through user testing)
- **SC-006**: The solver finds valid solutions for all correctly configured solvable puzzles (no false negatives)
- **SC-007**: The solver correctly identifies unsolvable configurations (no false positives)
- **SC-008**: 90% of users find the tabbed interface more usable than a split-pane design (verified through user testing)
- **SC-009**: The entire board is visible on screen without scrolling for all board sizes up to 50×50 cells
- **SC-010**: Users can switch between piece and board editing without losing context or having to resize windows

## Assumptions

- Polyomino pieces are made of connected square cells (common definition in tiling puzzles)
- The backtracking algorithm should explore all possible piece placements systematically
- Users have basic familiarity with grid-based drawing interfaces
- Puzzles are small enough that backtracking can find solutions in reasonable time (e.g., under 2 minutes for typical puzzles)
- Users want to understand the solving process, not just see the final result
- The visualization speed should be slow enough to follow but fast enough not to be tedious
- Precomputing all 8 transformations (4 rotations × 2 mirrors) before solving significantly improves solving performance compared to computing transformations on-demand
- Initially filled cells on the board create permanent obstacles that cannot be covered by puzzle pieces
- Board configurations with initially filled cells should be treated as distinct puzzle types from empty boards of the same dimensions
- Tabbed interface provides better usability by maximizing vertical space for grid editing
- Auto-resizing grids ensures the entire board/piece is visible regardless of dimensions
- Piece colors are generated dynamically during visualization and do not need to be persisted with piece definitions
- Consistent interaction patterns (click, drag, right-click) across both editors reduces cognitive load

## Out of Scope

- Pre-defined puzzle libraries or templates
- Automatic piece generation or puzzle generation algorithms
- Solving optimization beyond basic backtracking (e.g., heuristics, pruning strategies, parallel solving)
- Advanced features like piece mirroring or non-rectangular board shapes (note: flipping is allowed per FR-016)
- Mobile or web interfaces
- Performance optimization for very large puzzles (100+ cells)
- Save/load functionality beyond JSON file-based export/import (e.g., databases, cloud sync)
- Multi-user or collaborative features
- Analysis tools (e.g., move counting, time statistics)
