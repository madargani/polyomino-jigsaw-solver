---

description: "Task list for Polyomino Puzzle Solver feature implementation"
---

# Tasks: Polyomino Puzzle Solver

**Input**: Design documents from `/specs/001-polyomino-puzzle-solver/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL but recommended for this feature. Test tasks are included below using pytest framework.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan (src/models/, src/logic/, src/gui/, src/utils/, tests/unit/, tests/integration/, tests/fixtures/)
- [x] T002 Initialize Python 3.11+ project with PySide6, pytest, pytest-qt, pytest-mock dependencies
- [x] T003 [P] Create requirements.txt with PySide6, pytest, pytest-qt, pytest-mock, flake8, mypy, black, radon
- [x] T004 [P] Configure pytest in pytest.ini with discovery for tests/unit/ and tests/integration/
- [x] T005 [P] Configure flake8 for linting in .flake8 (Note: Using ruff instead - see .ruffignore)
- [x] T006 [P] Configure mypy for type checking in mypy.ini (Note: Configured in pyproject.toml)
- [x] T007 [P] Configure black for code formatting in pyproject.toml
- [x] T008 Create README.md with installation and quickstart instructions
- [x] T009 Create .gitignore for Python project (venv/, __pycache__/, .pytest_cache/, *.pyc, .mypy_cache/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Implement PuzzlePiece class with shape attribute (color generated dynamically during visualization) in src/models/piece.py
- [x] T011 Implement GameBoard class with width, height, cells attributes in src/models/board.py
- [x] T012 Implement PuzzleState class with board, placed_pieces, backtrack_history in src/models/puzzle_state.py
- [x] T013 Implement PuzzleConfiguration class with name, board_width, board_height, pieces in src/models/puzzle_config.py
- [x] T014 Implement rotation and flip operations in src/logic/rotation.py
- [x] T015 Implement piece and puzzle validation logic in src/logic/validator.py
- [x] T016 Create sample puzzle fixtures in tests/fixtures/sample_puzzles.json

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅ COMPLETED

---

## Phase 3: User Story 1 - Define Puzzle Configuration (Priority: P1) 🎯 MVP

**Goal**: User can launch application and define puzzle pieces and board shape through a graphical grid editor

**Independent Test**: Launch application, draw a simple piece shape, set board dimensions (e.g., 5x5), and verify the configuration persists in memory. No solving or visualization required.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T017 [P] [US1] Unit test for PuzzlePiece creation, rotation, shape validation (no color validation needed) in tests/unit/test_piece.py
- [x] T018 [P] [US1] Unit test for GameBoard operations, placement checks in tests/unit/test_board.py
- [x] T019 [P] [US1] Unit test for rotation and flip operations in tests/unit/test_rotation.py
- [x] T020 [P] [US1] Unit test for validator logic (contiguity, bounds, overlap) in tests/unit/test_validator.py
- [x] T021 [P] [US1] Integration test for puzzle configuration creation and validation in tests/integration/test_puzzle_config.py

### Implementation for User Story 1

- [x] T022 [P] [US1] Create main application entry point in src/main.py
- [x] T023 [US1] Create EditorWindow class with tabbed interface (Pieces tab, Board tab) in src/gui/editor_window.py
- [x] T024 [P] [US1] Create BoardTab grid editor component with auto-resize to fit screen in src/gui/board_tab.py
- [x] T025 [P] [US1] Create PieceTab for piece drawing with consistent interaction patterns (click, drag, right-click) in src/gui/piece_tab.py
- [x] T026 [US1] Implement grid-based piece drawing with mouse interaction (left-click to add, drag to paint, right-click to toggle) in src/gui/piece_tab.py
- [x] T027 [US1] Implement board dimension input controls with auto-resize in src/gui/editor_window.py
- [x] T028 [US1] Implement piece list display and selection in src/gui/editor_window.py
- [x] T029 [US1] Implement piece add/delete functionality in src/gui/editor_window.py
- [x] T030 [US1] Implement puzzle configuration state management in src/models/puzzle_config.py
- [x] T031 [US1] Integrate tabbed editor interface in src/gui/editor_window.py
- [x] T032 [US1] Implement dynamic color generation for each piece type during visualization in src/utils/color_generator.py
- [x] T033 [US1] Add validation feedback display in src/gui/editor_window.py

**Checkpoint**: User Story 1 COMPLETED ✅ - User can launch app, draw pieces, set board dimensions, and see configuration in editor. All 124 tests passing.

---

## Phase 4: User Story 2 - Solve Puzzle Visualization (Priority: P2)

**Goal**: User can click Solve button to open visualization window showing real-time backtracking algorithm attempting to place pieces using generator-based approach with QTimer

**Independent Test**: Define a simple solvable puzzle (e.g., 2x2 board with two L-shaped trominoes), click solve, and verify visualization window opens showing board with pieces being placed and backtracked when dead ends occur.

**Architecture Note**: Uses generator function pattern with QTimer instead of threading, eliminating thread synchronization complexity.

### Tests for User Story 2

- [x] T034 [P] [US2] Unit test for solve_backtracking() generator in tests/unit/test_solver.py
- [x] T035 [P] [US2] Unit test for generator yield format and state snapshots in tests/unit/test_solver.py
- [x] T036 [P] [US2] Integration test for end-to-end puzzle solve with generator in tests/integration/test_puzzle_flow.py
- [x] T037 [P] [US2] GUI handler test for solve button and QTimer management in tests/unit/test_gui_handlers.py

### Implementation for User Story 2

- [x] T038 [P] [US2] Implement solve_backtracking() generator function in src/logic/solver.py
- [x] T039 [US2] Implement backtracking algorithm with orientation generation in generator in src/logic/solver.py
- [x] T040 [US2] Implement generator yield format with state snapshots in src/logic/solver.py
- [x] T041 [US2] Implement StopIteration handling for solution/no_solution in src/logic/solver.py
- [x] T042 [P] [US2] Create VizWindow for solver visualization in src/gui/viz_window.py
- [x] T043 [P] [US2] Create board visualization view in src/gui/viz_window.py
- [x] T044 [US2] Implement QTimer-based generator consumption in src/gui/viz_window.py
- [x] T045 [US2] Implement speed control via QTimer interval adjustment in src/gui/viz_window.py
- [x] T046 [US2] Implement real-time board update visualization from generator yields in src/gui/viz_window.py
- [x] T047 [US2] Implement solution found / no solution found detection in src/gui/viz_window.py
- [x] T048 [US2] Implement stop/interrupt solver via generator.close() in src/gui/viz_window.py
- [x] T049 [US2] Integrate solve button in editor window with viz window launch in src/gui/editor_window.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. User can define puzzle and watch solver visualize backtracking in real-time using generator + QTimer architecture. ✅ US2 COMPLETED

---

## Phase 5: User Story 3 - Puzzle Management (Priority: P3)

**Goal**: User can save, load, clear, export, and import puzzle configurations using JSON format

**Independent Test**: Create a puzzle configuration, save it with a name, clear the editor, load the saved puzzle, and verify the configuration matches what was saved. Also test export/import by exporting to file and importing it back.

### Tests for User Story 3

- [x] T051 [P] [US3] Unit test for save_puzzle function in tests/unit/test_file_io.py
- [x] T052 [P] [US3] Unit test for load_puzzle function in tests/unit/test_file_io.py
- [x] T053 [P] [US3] Unit test for export_puzzle function in tests/unit/test_file_io.py
- [x] T054 [P] [US3] Unit test for import_puzzle function in tests/unit/test_file_io.py
- [x] T055 [P] [US3] Integration test for save/load roundtrip in tests/integration/test_file_io.py
- [x] T056 [P] [US3] Integration test for export/import roundtrip in tests/integration/test_file_io.py

### Implementation for User Story 3

- [x] T057 [P] [US3] Implement save_puzzle function in src/utils/file_io.py
- [x] T058 [P] [US3] Implement load_puzzle function in src/utils/file_io.py
- [x] T059 [P] [US3] Implement export_puzzle function in src/utils/file_io.py
- [x] T060 [P] [US3] Implement import_puzzle function in src/utils/file_io.py
- [x] T061 [US3] Implement JSON serialization in PuzzleConfiguration.to_dict() in src/models/puzzle_config.py
- [x] T062 [US3] Implement JSON deserialization in PuzzleConfiguration.from_dict() in src/models/puzzle_config.py
- [x] T063 [US3] Implement save puzzle dialog and action in src/gui/editor_window.py
- [x] T064 [US3] Implement load puzzle dialog and action in src/gui/editor_window.py
- [x] T065 [US3] Implement clear configuration functionality in src/gui/editor_window.py
- [x] T066 [US3] Implement export puzzle dialog and action in src/gui/editor_window.py
- [x] T067 [US3] Implement import puzzle dialog and action in src/gui/editor_window.py
- [x] T068 [US3] Implement saved puzzles list display in src/gui/editor_window.py

**Checkpoint**: All user stories should now be independently functional. User can define puzzles, visualize solving, and manage puzzle configurations. ✅ US3 COMPLETED

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T069 [P] Add comprehensive docstrings to all public functions and classes (PEP 257)
- [ ] T070 [P] Add type hints to all function signatures
- [ ] T071 [P] Run flake8 and fix all linting issues
- [ ] T072 [P] Run mypy and fix all type checking issues
- [ ] T073 [P] Run black to format all code
- [ ] T074 Check cyclomatic complexity with radon and refactor functions over 10
- [ ] T075 Add error handling and user-friendly error messages in GUI
- [ ] T076 Disable edit controls during solving and display notification in src/gui/editor_window.py
- [ ] T077 Add validation warnings for piece area vs board area mismatch in src/gui/editor_window.py
- [ ] T078 Add keyboard shortcuts for common actions (Save: Ctrl+S, Load: Ctrl+O, Solve: Ctrl+Enter)
- [ ] T079 Update README.md with complete usage instructions and screenshots
- [ ] T080 Run quickstart.md validation - verify all commands work
- [ ] T081 Add unit tests for edge cases (empty puzzles, max dimensions, overlapping pieces)
- [ ] T082 Add integration test for complete user workflow (create → solve → save → load)
- [ ] T083 Run all tests with coverage: `pytest --cov=src --cov-report=html`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Define Puzzle Configuration**:
  - Depends on: Foundational phase (models, rotation, validator)
  - No dependencies on other user stories
  - Can be implemented and tested independently

- **User Story 2 (P2) - Solve Puzzle Visualization**:
  - Depends on: Foundational phase + User Story 1 (editor window, puzzle configuration)
  - Integrates with US1 editor window for solve button
  - Should be independently testable for solver logic

- **User Story 3 (P3) - Puzzle Management**:
  - Depends on: Foundational phase + User Story 1 (editor window, puzzle configuration)
  - Integrates with US1 editor window for save/load UI
  - Should be independently testable for file I/O

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Models before services/logic
- Services/logic before GUI components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup Phase**: T003, T004, T005, T006, T007 can all run in parallel
- **Foundational Phase**: T010-T013 (models) can run in parallel
- **User Story 1 Tests**: T017-T021 can all run in parallel
- **User Story 1 Implementation**: T022-T025 can run in parallel (different files)
- **User Story 2 Tests**: T034-T037 can all run in parallel
- **User Story 2 Implementation**: T038, T042, T043 can run in parallel
- **User Story 3 Tests**: T051-T056 can all run in parallel
- **User Story 3 Implementation**: T057-T060 can run in parallel
- **Polish Phase**: T069-T073 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for PuzzlePiece creation, rotation, validation in tests/unit/test_piece.py"
Task: "Unit test for GameBoard operations, placement checks in tests/unit/test_board.py"
Task: "Unit test for rotation and flip operations in tests/unit/test_rotation.py"
Task: "Unit test for validator logic in tests/unit/test_validator.py"
Task: "Integration test for puzzle configuration creation and validation in tests/integration/test_puzzle_config.py"

# Launch all GUI components for User Story 1 together:
Task: "Create main application entry point in src/main.py"
Task: "Create EditorWindow class with tabbed interface (Pieces tab, Board tab) in src/gui/editor_window.py"
Task: "Create BoardTab grid editor component with auto-resize to fit screen in src/gui/board_tab.py"
Task: "Create PieceTab for piece drawing with consistent interaction patterns (click, drag, right-click) in src/gui/piece_tab.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T016) - **CRITICAL**
3. Complete Phase 3: User Story 1 (T017-T033)
4. **STOP and VALIDATE**:
    - Launch application: `python -m src.main`
    - Switch between "Pieces" and "Board" tabs to verify tabbed interface works
    - Draw a piece shape on the grid using left-click, drag, right-click interactions
    - Set board dimensions to 5x5 and verify grid auto-resizes to fit screen
    - Add another piece
    - Verify pieces are listed and can be selected
    - Delete a piece and verify it's removed
5. Demo: Show users can define puzzle configurations using tabbed editor
6. **MVP DELIVERED**: Core value proposition achieved

### Incremental Delivery

1. **MVP Cycle** (as above): Setup → Foundational → US1 → Deploy/Demo
2. **Add User Story 2**: Complete T034-T050 → Test independently → Deploy/Demo
   - Define puzzle → Click Solve → Watch visualization
3. **Add User Story 3**: Complete T051-T068 → Test independently → Deploy/Demo
   - Save puzzle → Clear editor → Load puzzle → Verify
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers (2-3 developers recommended):

1. **Week 1**: All developers complete Setup + Foundational together (T001-T016)
2. **Week 2-3**: Once Foundational is done, split by user story:
   - Developer A: User Story 1 (Define Puzzle) - T017-T033
   - Developer B: User Story 2 (Solver Visualization) - T034-T050
   - Developer C: User Story 3 (Puzzle Management) - T051-T068
3. **Week 4**: Integration testing and Polish (T069-T083)
4. Stories complete and integrate independently with minimal conflicts

---

## Spec Updates (2026-01-16)

The following changes were made to align with updated design requirements:

- **Tabbed Interface**: Editor uses separate "Pieces" and "Board" tabs to maximize vertical screen space (T023, T031)
- **Auto-resize Grids**: Both piece and board editors automatically resize to fit within visible screen area (T024, T027)
- **Consistent Interaction**: Both editors use identical interaction patterns (left-click, drag, right-click) (T025, T026)
- **Dynamic Colors**: Piece colors are generated during visualization, not stored with piece definitions (T010, T032)

---

## Format Validation

✅ **All tasks follow strict checklist format**:
- Checkbox: `- [ ]` present on every task
- Task ID: Sequential (T001, T002, T003...) in execution order
- [P] marker: Included for parallelizable tasks
- [Story] label: [US1], [US2], [US3] for user story phase tasks
- Description: Clear action with exact file path

**Task Count Summary**:
- Total tasks: 83
- Phase 1 (Setup): 9 tasks - ✅ COMPLETED
- Phase 2 (Foundational): 7 tasks - ✅ COMPLETED
- Phase 3 (US1): 17 tasks (5 tests + 12 implementation) - ✅ COMPLETED
- Phase 4 (US2): 17 tasks (4 tests + 13 implementation) - ✅ COMPLETED
- Phase 5 (US3): 18 tasks (6 tests + 12 implementation) - ✅ COMPLETED
- Phase 6 (Polish): 15 tasks - PENDING

**Progress**: 68/83 tasks completed (82%)

**Parallel Opportunities**: 34 tasks marked with [P] can be run in parallel across different phases and within phases.

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach recommended)
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- User Story 1 is MVP - complete and validate before proceeding to US2/US3
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Testing is recommended but optional - test tasks are included for completeness
