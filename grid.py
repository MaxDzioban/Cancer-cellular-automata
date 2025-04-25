"""grid.py"""
import numpy as np
from numpy.typing import NDArray


class Grid:
    """Class representing a grid of cells."""
    def __init__(self, rows: int, cols: int):
        self.rows: int = rows
        self.cols: int = cols
        self.grid: NDArray = np.zeros(shape=(self.rows, self.cols), dtype=bool)
        self.cells: dict[tuple[int, int]: "Cell"] = {}

    @property
    def num_cells(self) -> int:
        """Return the number of cells in the grid."""
        return len(self.cells)

    def add_cell(self, cell):
        """Add a cell to the grid."""
        x, y = cell.position
        if 0 <= x < self.rows and 0 <= y < self.cols:
            self.grid[x, y] = True
            self.cells[cell.position] = cell
        else:
            raise ValueError("Cell position out of bounds.")

    def remove_cell(self, cell):
        """Remove a cell from the grid."""
        x, y = cell.position
        if (x, y) in self.cells:
            self.grid[x, y] = False
            del self.cells[(x, y)]
        else:
            raise ValueError("Cell not found in grid.")

    def move_cell(self, cell, new_position: tuple[int, int]):
        """Move a cell to a new position on the grid."""
        x, y = cell.position
        new_x, new_y = new_position
        if (new_x, new_y) in self.cells:
            raise ValueError("New position already occupied by another cell.")
        if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
            self.grid[x, y] = False
            self.grid[new_x, new_y] = True
            del self.cells[(x, y)]
            cell.position = new_position
            self.cells[new_position] = cell
        else:
            raise ValueError("New position out of bounds.")

    def empty_neighbors(self, cell) -> list[tuple[int, int]]:
        """Return a list of empty neighboring positions for a given cell."""
        x, y = cell.position
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
                    if not self.grid[new_x, new_y]:
                        neighbors.append((new_x, new_y))
        return neighbors

    def empty_grid(self):
        """Empty the grid."""
        self.grid.fill(False)
        self.cells.clear()

    def fill_grid(self, cells: dict[tuple[int, int]: "Cell"]):
        """Fill the grid with a list of cells."""
        for cell in cells:
            self.add_cell(cell)

    def make_action(self):
        """Make action for each cell in the grid."""
        cells = list(self.cells.values())
        for cell in cells:
            cell.make_action(self)

    def remove_cell_at(self, position):
        if position in self.cells:
            self.remove_cell(self.cells[position])
