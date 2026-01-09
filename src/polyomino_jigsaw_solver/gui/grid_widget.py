from typing import Callable, FrozenSet, Optional

import customtkinter as ctk


class GridWidget(ctk.CTkFrame):
    def __init__(
        self,
        master,
        rows: int,
        cols: int,
        cell_size: int = 30,
        initial_state: FrozenSet[tuple[int, int]] = frozenset(),
        on_change: Optional[Callable[[FrozenSet[tuple[int, int]]], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.state: set[tuple[int, int]] = set(initial_state)
        self.on_change = on_change

        self.canvas = ctk.CTkCanvas(
            self,
            width=cols * cell_size,
            height=rows * cell_size,
            bg="#1a1a2e",
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=10)

        self.canvas.bind("<Button-1>", self._on_click)
        self._draw_grid()

    def _on_click(self, event) -> None:
        x = event.x // self.cell_size
        y = event.y // self.cell_size

        if 0 <= x < self.cols and 0 <= y < self.rows:
            cell = (x, y)
            if cell in self.state:
                self.state.remove(cell)
            else:
                self.state.add(cell)
            self._draw_grid()

            if self.on_change is not None:
                self.on_change(frozenset(self.state))

    def _draw_grid(self) -> None:
        self.canvas.delete("all")

        # Draw cell backgrounds
        for x, y in self.state:
            x1 = x * self.cell_size
            y1 = y * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#4a90e2", outline="")

        # Draw grid lines
        for i in range(self.rows + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.cols * self.cell_size, y, fill="#2d2d44")

        for i in range(self.cols + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.rows * self.cell_size, fill="#2d2d44")

    def set_state(self, state: FrozenSet[tuple[int, int]]) -> None:
        self.state = set(state)
        self._draw_grid()

    def get_state(self) -> FrozenSet[tuple[int, int]]:
        return frozenset(self.state)

    def clear(self) -> None:
        self.state.clear()
        self._draw_grid()

        if self.on_change is not None:
            self.on_change(frozenset())
