"""grid.py"""
import random
import numpy as np
from numpy.typing import NDArray
from immune_utils import recruit_immune_cells
import random
from cells import ImmuneCell

class Grid:
    """Class representing a grid of cells."""
    def __init__(self, rows: int, cols: int):
        self.rows: int = rows
        self.cols: int = cols
        self.grid: NDArray = np.zeros(shape=(self.rows, self.cols), dtype=bool)
        self.cells: dict[tuple[int, int]: "Cell"] = {}
        self.kill_count = 0
        self.failure_count= 0
        self.immune_spawn = 0.001



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

    def remove_cell_at(self, position):
        """Remove a cell at a specific position."""
        if position in self.cells:
            self.remove_cell(self.cells[position])

    def move_cell(self, cell, new_position: tuple[int, int]):
        """Move a cell to a new position on the grid."""
        x, y = cell.position
        new_x, new_y = new_position
        if (new_x, new_y) in self.cells:
            raise ValueError("New position already occupied by another cell.")
        if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
            self.grid[x, y] = False
            self.grid[new_x, new_y] = True
            # Add a check to make sure the cell position exists before deleting
            if (x, y) in self.cells:
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

    def apply_chemotherapy(self):
        """Apply chemotherapy to all cells in the grid."""
        cells = list(self.cells.values())
        for cell in cells:
            cell.apply_chemotherapy(self)
    
    def apply_immunotherapy(self):
        """Apply immunotherapy to all immune cells in the grid."""
        self.immune_spawn *=2
        for cell in self.cells.values():
            if isinstance(cell, ImmuneCell):
                cell.apply_immunotherapy()
    
    def reset_all_immune_cells(self):
        """Reset parameters of all immune cells in the grid."""
        self.immune_spawn /=2
        for cell in self.cells.values():
            if isinstance(cell, ImmuneCell):
                cell.reset_immunotherapy()
    

    def spawn_possible_cell(self, i, j):
        """Spawn a possible immune cell with weighted random type at (i, j)."""
        spell_type = random.choices([0, 1], weights=[0.7, 0.3])[0]  # 70% для 0, 30% для 1
        new_cell = ImmuneCell((i, j), spell_type)
        self.add_cell(new_cell)
    

    def make_action(self):
        """Make action for each cell in the grid."""
        for i, line in enumerate(self.grid):
            for j, cell in enumerate(line):
                if cell:
                    self.cells[(i, j)].make_action(self)


        rows = len(self.grid)
        cols = len(self.grid[0]) if rows > 0 else 0

        for j in range(cols):
            for i in [0, rows - 1]:
                if not self.grid[i, j] and random.random() < self.immune_spawn:
                    self.spawn_possible_cell(i, j)


        for i in range(1, rows - 1):
            for j in [0, cols - 1]:
                if not self.grid[i, j] and random.random() < self.immune_spawn:
                    self.spawn_possible_cell(i, j)
        # recruit_immune_cells(self, self.kill_count, self.failure_count)
        self.kill_count = 0
        self.failure_count= 0


    def neighbors(self, cell) -> list[tuple[int, int]]:
        """Return a list of neighboring positions for a given cell."""
        x, y = cell.position
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
                    if (new_x, new_y) in self.cells:
                        neighbors.append(self.cells[(new_x, new_y)])
        return neighbors

    
    def count_cells(self, cell_types : tuple):
        """Count the number of cells of a specific type in the grid."""
        count = 0
        for cell in self.cells.values():
            if isinstance(cell_types, tuple):
                for cell_type in cell_types:
                    if isinstance(cell, cell_type):
                        count += 1
            else:
                if isinstance(cell, cell_types):
                    count += 1
        return count

    def empty_cells(self):
        """Return a list of empty positions in the grid."""
        empty = []
        for y in range(self.rows):
            for x in range(self.cols):
                if not self.grid[y][x]:
                    empty.append((y, x))
        return empty

    def nearest_tumor_distance(self, position):
        """Return the distance from the given position to the nearest tumor cell."""
        min_dist = float('inf')
        for cell in self.cells.values():
            if cell.is_tumor_cell:
                dist = np.sqrt((position[0] - cell.position[0]) ** 2 + (position[1] - cell.position[1]) ** 2)
                if dist < min_dist:
                    min_dist = dist
        return min_dist

    def get_random_empty_position(self):
        """Find a random empty spot on the grid"""
        empty = [(i, j) for i in range(self.rows) for j in range(self.cols) if not self.grid[i, j]]
        return random.choice(empty) if empty else None
