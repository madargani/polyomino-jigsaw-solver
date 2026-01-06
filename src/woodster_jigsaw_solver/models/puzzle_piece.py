from dataclasses import dataclass
from typing import FrozenSet, Iterable, List, Tuple


@dataclass(frozen=True)
class PuzzlePiece:
    transformations: FrozenSet[FrozenSet[Tuple[int, int]]]

    def __init__(self, coordinates: Iterable[Tuple[int, int]]):
        coords_list = list(coordinates)
        transformations = self._generate_transformations(coords_list)
        normalized = [self._normalize(t) for t in transformations]
        unique_frozensets = set(frozenset(t) for t in normalized)
        object.__setattr__(self, "transformations", frozenset(unique_frozensets))

    def _generate_transformations(
        self, coords: List[Tuple[int, int]]
    ) -> List[List[Tuple[int, int]]]:
        transformations: List[List[Tuple[int, int]]] = []

        for flip in [False, True]:
            current = coords[:]
            for _ in range(4):
                transformations.append(current)
                current = self._rotate(current)
            if flip:
                transformations.append(self._flip(coords))

        return transformations

    def _rotate(self, coords: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        return [(-y, x) for x, y in coords]

    def _flip(self, coords: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        return [(-x, y) for x, y in coords]

    def _normalize(self, coords: List[Tuple[int, int]]) -> Tuple[Tuple[int, int], ...]:
        if not coords:
            return ()

        min_x = min(x for x, _ in coords)
        min_y = min(y for _, y in coords)

        normalized = sorted((x - min_x, y - min_y) for x, y in coords)
        return tuple(normalized)

    def ascii_diagram(self) -> str:
        coords = next(iter(self.transformations))
        if not coords:
            return ""

        max_x = max(x for x, _ in coords)
        max_y = max(y for _, y in coords)

        grid = [[" " for _ in range(max_x + 1)] for _ in range(max_y + 1)]

        for x, y in coords:
            grid[y][x] = "█"

        return "\n".join("".join(row) for row in grid)
