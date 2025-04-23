"""cells.py"""
import random


class Cell:
    """Class representing a cell in a grid."""
    RATES = { 'apoptosis': None, 'proliferation': None, 'migration': None}

    def __init__(self, position: tuple[int, int]):
        """Initialize the cell with coordinates on a grid"""
        self.position = position  # Tuple of (x, y) coordinates on a grid

    @classmethod
    def set_rates(cls, apoptosis: float, proliferation: float, migration: float):
        """Set the rates for the cell's actions."""
        if not 0 < (apoptosis+proliferation+migration) <= 1:
            raise ValueError("Rates must sum must be between 0 and 1.")

        cls.RATES['apoptosis'] = apoptosis
        cls.RATES['proliferation'] = proliferation
        cls.RATES['migration'] = migration

    def make_action(self, grid):
        """Determine the action of the cell based on its rates."""
        if random.random() <= self.RATES['apoptosis']:
            self.apoptosis(grid)
        elif random.random() <= self.RATES['proliferation']:
            self.proliferation(grid)
        elif random.random() <= self.RATES['migration']:
            self.migration(grid)
        else:
            self.quiscence()

    def __die(self, grid):
        """Cell dies."""
        grid.remove_cell(self)

    def apoptosis(self, grid):
        """Cell undergoes apoptosis."""
        self.__die(grid)

    def proliferation(self, grid):
        """Cell proliferates to an empty neighboring cell."""
        print(f"Cell at {self.position} proliferates.")
        empty_neighbors = grid.empty_neighbors(self)
        if empty_neighbors:
            new_position = random.choice(empty_neighbors)
            new_cell = Cell(new_position)
            grid.add_cell(new_cell)
        else:
            print("No empty neighbors to proliferate to.")

    def migration(self, grid):
        """Cell migrates to an empty neighboring cell."""
        print(f"Cell at {self.position} migrates.")
        empty_neighbors = grid.empty_neighbors(self)
        if empty_neighbors:
            new_position = random.choice(empty_neighbors)
            grid.move_cell(self, new_position)
        else:
            print("No empty neighbors to migrate to.")

    def quiscence(self):
        """Cell remains quiescent."""
        print(f"Cell at {self.position} remains quiescent.")
