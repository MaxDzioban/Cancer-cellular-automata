"""cells.py"""
import random
import grid

class Cell:
    """Class representing a cell in a grid."""
    RATES = { 'apoptosis': None, 'proliferation': None, 'migration': None}

    def __init__(self, position: tuple[int, int]):
        """Initialize the cell with coordinates on a grid"""
        self.position = position  # Tuple of (x, y) coordinates on a grid
        self.is_tumor_cell = False 

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

class RegularTumorCell(Cell):
    """Class representing a regular tumor cell."""
    def __init__(self, position: tuple[int, int]):
        """Initialize the regular tumor cell ."""
        super().__init__(position)
        self.p_remaining = 5 
        self.set_rates(apoptosis=0.1, proliferation=0.3, migration=0.2)
        self.is_tumor_cell = True 
    
    def proliferation(self, grid):
        """RTC divides to empty neighboring position if p_remaining > 0."""
        if self.p_remaining > 0:
            empty_neighbors = grid.empty_neighbors(self)
            if empty_neighbors:
                new_position = random.choice(empty_neighbors)
                new_cell = RegularTumorCell(new_position)
                new_cell.p_remaining = self.p_remaining - 1
                grid.add_cell(new_cell)
                self.p_remaining -= 1

class StemTumorCell(Cell):
    """Class representing a stem tumor cell."""
    def __init__(self, position: tuple[int, int]):
        """Initialize the stem tumor cell."""
        super().__init__(position)
        self.set_rates(apoptosis=0.0, proliferation=0.4, migration=0.1)
        self.is_tumor_cell = True

    def proliferation(self, grid):
        """CSC can divide symmetrically or asymmetrically."""
        empty_neighbors = grid.empty_neighbors(self)
        if empty_neighbors:
            new_position = random.choice(empty_neighbors)
            if random.random() <= 0.5:  
                new_cell = StemTumorCell(new_position)
            else:
                new_cell = RegularTumorCell(new_position)
            grid.add_cell(new_cell)

class ImmuneCell(Cell):
    """Class representing an immune cell."""
    def __init__(self, position: tuple[int, int],cell_type: int):
        """Initialize the immune cell with coordinates on a grid."""
        super().__init__(position)
        self.set_rates(0.2, 0.1, 0.3)
        self.cell_type = cell_type
        self.kill_count = 0
        self.failure_count = 0
    
    
    def attack(self, target_cell, grid):
        """Immune cell attacks a tumor cell."""
        neighbors = grid.neighbors(self)
        immune_neighbors = [cell for cell in neighbors if isinstance(cell, ImmuneCell)]
        tumor_neighbors = [cell for cell in neighbors if isinstance(cell, (RegularTumorCell, StemTumorCell))]
        n_I1 = len(immune_neighbors)
        n_PT1 = len(tumor_neighbors)
        if n_PT1 == 0:
            r_I = 0
        else:
            K0 = 0.5
            r_I = K0 * (n_I1 / n_PT1)

            if isinstance(target_cell, StemTumorCell):
                r_I *= 0.2
            elif isinstance(target_cell, RegularTumorCell):
                r_I *= 1.0
        r_I = min(r_I, 1.0)

        if random.random() <= r_I:
            grid.remove_cell(target_cell)
            return True
        return False

    def migration(self, grid):
        """Immune cell migrates to the nearest empty cell."""
        empty_neighbors = grid.empty_neighbors(self)
        if not empty_neighbors:
            return
        min_dist = float('inf')
        best_pos = None
        for pos in empty_neighbors:
            dist = grid.nearest_tumor_distance(pos)
            if dist < min_dist:
                min_dist = dist
                best_pos = pos

        if best_pos:
            grid.move_cell(self, best_pos)

    def get_failure_death_prob(self, grid):
        """Calculate the probability of death for the immune cell."""
        neighbors = grid.neighbors(self)
        immune_neighbors = [cell for cell in neighbors if isinstance(cell, ImmuneCell)]
        tumor_neighbors = [cell for cell in neighbors if isinstance(cell, (RegularTumorCell, StemTumorCell))]
        n_I1 = len(immune_neighbors)
        n_PT1 = len(tumor_neighbors)
        if n_I1 == 0:
            return 1.0
        else:
            K1 = 0.2
            r_t = K1 * (n_PT1 / n_I1)
            return min(r_t, 1.0)
    
    def proliferation(self, grid):
        """Immune cell proliferates to an empty neighboring cell."""
        killed_cells = self.kill_count
        failed_cells= self.failure_count

        if killed_cells == 0:
            return  

        nT = grid.count_cells((RegularTumorCell, StemTumorCell))
        nPT = grid.count_cells(RegularTumorCell)

        if nT == 0:
            return

        newborns = int((killed_cells - failed_cells) * (nPT / nT))

        if newborns > 0:
            empty_cells = grid.empty_cells()
            for _ in range(min(newborns, len(empty_cells))):
                position = random.choice(empty_cells)
                new_cell = ImmuneCell(position, cell_type='CTL')  # CTL створюємо
                grid.add_cell(new_cell)
                empty_cells.remove(position)
            self.kill_count = 0
            self.failure_count = 0

    def make_action(self, grid):
        """Make action for the immune cell."""
        neighbors = grid.neighbors(self)
        tumor_neighbors = [cell for cell in neighbors if isinstance(cell, (RegularTumorCell, StemTumorCell))]
        if tumor_neighbors:
            if self.cell_type == 1:
                for target in tumor_neighbors:
                    result = self.attack(target, grid)
                    if result:
                        self.kill_count += 1
                    else:
                        self.failure_count += 1
                        death_prob = self.get_failure_death_prob(grid)
                        if random.random() <= death_prob:
                            grid.remove_cell(self)
                            return
            elif self.cell_type == 0:
                target = random.choice(tumor_neighbors)
                result = self.attack(target, grid)
                if result:
                    self.kill_count += 1
                    grid.remove_cell(self)

                else:
                    self.failure_count += 1
                    death_prob = self.get_failure_death_prob(grid)
                    if random.random() <= death_prob:
                        grid.remove_cell(self)
        else:
            self.migration(grid)
        self.proliferation(grid)
        
