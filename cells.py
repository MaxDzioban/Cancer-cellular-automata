"""cells.py"""
import random

class Cell:
    """Class representing a cell in a grid."""
    RATES = { 'apoptosis': 0.0, 'proliferation': 0.0, 'migration': 0.0 }
    PROLIFERATION_DECREASE = 0.05
    DEATH_CHEMOTERAPY_CHANCE = 0.02

    def __init__(self, position: tuple[int, int], proliferation_decrease_coef: float=0.0):
        """Initialize the cell with coordinates on a grid"""
        self.position = position  # Tuple of (x, y) coordinates on a grid
        self.is_tumor_cell = False
        self.proliferation_decrease_coef = proliferation_decrease_coef

    @classmethod
    def set_rates(cls, apoptosis_rate: float, proliferation_rate: float, migration_rate: float):
        """
        Set the rates for the cell's actions.

        Summ of rates must be between 0 and 1.
        Args:
            apoptosis_rate (float): Chance of cell to undergo apoptosis at each step.
            proliferation_rate (float): Chance of cell to proliferate at each step.
            migration_rate (float): Chance of cell to migrate at each step.
        """
        cls.RATES['apoptosis'] = apoptosis_rate
        cls.RATES['proliferation'] = proliferation_rate
        cls.RATES['migration'] = migration_rate

    def make_action(self, grid):
        """Determine the action of the cell based on its rates."""
        if random.random() <= self.RATES['apoptosis']:
            self.apoptosis(grid)
        elif random.random() <= self.RATES['proliferation'] * (1-self.proliferation_decrease_coef):
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
        # print(f"Cell at {self.position} proliferates.")
        empty_neighbors = grid.empty_neighbors(self)
        if empty_neighbors:
            new_position = random.choice(empty_neighbors)
            new_cell = Cell(new_position, self.proliferation_decrease_coef)
            grid.add_cell(new_cell)

    def migration(self, grid):
        """Cell migrates to an empty neighboring cell."""
        # print(f"Cell at {self.position} migrates.")
        # empty_neighbors = grid.empty_neighbors(self)
        # if empty_neighbors:
        #     new_position = random.choice(empty_neighbors)
        #     grid.move_cell(self, new_position)
        # else:
        #     print("No empty neighbors to migrate to.")
        pass

    def quiscence(self):
        """Cell remains quiescent."""
        # print(f"Cell at {self.position} remains quiescent.")

    def apply_chemotherapy(self, grid):
        """Apply chemotherapy to the cell."""
        self.proliferation_decrease_coef += self.PROLIFERATION_DECREASE
        # print(self.proliferation_decrease_coef)
        # if self.proliferation_decrease_coef >= 1:
            # self.apoptosis(grid)
            # return
        if random.random() <= self.DEATH_CHEMOTERAPY_CHANCE:
            self.apoptosis(grid)


class RegularTumorCell(Cell):
    """Class representing a regular tumor cell."""
    RATES = { 'apoptosis': 0.0, 'proliferation': 0.0, 'migration': 0.0 }
    MAX_DIVISIONS = 5
    PROLIFERATION_DECREASE = 0.05
    DEATH_CHEMOTERAPY_CHANCE = 0.02

    def __init__(self, position: tuple[int, int], proliferation_decrease_coef: float=0.0, p_remaining: int=MAX_DIVISIONS):
        """Initialize the regular tumor cell."""
        super().__init__(position, proliferation_decrease_coef)
        self.p_remaining = p_remaining
        # Number of divisions remaining

        self.is_tumor_cell = True

    @classmethod
    def set_constants(cls, apoptosis_rate: float,
                    proliferation_rate: float,
                    migration_rate: float,
                    max_divisions: int,
                    proliferation_decrease_coef: float,
                    death_chemotherapy_chance: float):
        """
        Set the constants for the regular tumor cell.
        
        Args:
            Summ of rates must be between 0 and 1.
            apoptosis_rate (float): Chance of cell to undergo apoptosis at each step.
            proliferation_rate (float): Chance of cell to proliferate at each step.
            migration_rate (float): Chance of cell to migrate at each step.

            max_divisions (int): Maximum number of divisions for the cell.
            proliferation_decrease_coef (float): Coefficient for decreasing proliferation chance
            after applying chemotherapy, must be between 0 and 1.
            death_chemotherapy_chance (float): Chance of cell death due to chemotherapy,
            must be between 0 and 1.
        """

        if not 0 < (apoptosis_rate+proliferation_rate+migration_rate) <= 1:
            raise ValueError("Rates must sum must be between 0 and 1.")
        if not 0 <= proliferation_decrease_coef <= 1:
            raise ValueError("Proliferation decrease coefficient must be between 0 and 1.")
        if not 0 <= death_chemotherapy_chance <= 1:
            raise ValueError("Death chemotherapy chance must be between 0 and 1.")

        cls.set_rates(apoptosis_rate, proliferation_rate, migration_rate)

        cls.MAX_DIVISIONS = max_divisions
        cls.PROLIFERATION_DECREASE = proliferation_decrease_coef
        cls.DEATH_CHEMOTERAPY_CHANCE = death_chemotherapy_chance

    def proliferation(self, grid):
        """RTC divides to empty neighboring position if p_remaining > 0."""
        if self.p_remaining == 0:
            return

        empty_neighbors = grid.empty_neighbors(self)
        if empty_neighbors:
            new_position = random.choice(empty_neighbors)
            self.p_remaining -= 1
            new_cell = RegularTumorCell(new_position, self.proliferation_decrease_coef, self.p_remaining)
            grid.add_cell(new_cell)


class StemTumorCell(Cell):
    """Class representing a stem tumor cell."""
    RATES = { 'apoptosis': 0.0, 'proliferation': 0.0, 'migration': 0.0 }
    PROLIFERATION_DECREASE = 0.05
    DEATH_CHEMOTERAPY_CHANCE = 0.02

    def __init__(self, position: tuple[int, int], proliferation_decrease_coef: float=0.0):
        """Initialize the stem tumor cell."""
        super().__init__(position, proliferation_decrease_coef)
        self.is_tumor_cell = True

    @classmethod
    def set_constants(cls, apoptosis_rate: float,
                    proliferation_rate: float,
                    migration_rate: float,
                    symmetrical_division_rate: float,
                    proliferation_decrease_coef: float,
                    death_chemotherapy_chance: float):
        """
        Set the constants for the stem tumor cell.

        Args:
            Summ of rates must be between 0 and 1.
            apoptosis_rate (float): Chance of cell to undergo apoptosis at each step.
            proliferation_rate (float): Chance of cell to proliferate at each step.
            migration_rate (float): Chance of cell to migrate at each step.

            symmetrical_division_rate (float): Chance of cell to divide symmetrically (produce one new STC),
            must be between 0 and 1.
            proliferation_decrease_coef (float): Coefficient for decreasing proliferation chance
            after applying chemotherapy, must be between 0 and 1.
            death_chemotherapy_chance (float): Chance of cell death due to chemotherapy,
            must be between 0 and 1.
        """

        if not 0 < (apoptosis_rate+proliferation_rate+migration_rate) <= 1:
            raise ValueError("Rates must sum must be between 0 and 1.")
        if not 0 <= symmetrical_division_rate <= 1:
            raise ValueError("Asymmetrical division rate must be between 0 and 1.")
        if not 0 <= proliferation_decrease_coef <= 1:
            raise ValueError("Proliferation decrease coefficient must be between 0 and 1.")
        if not 0 <= death_chemotherapy_chance <= 1:
            raise ValueError("Death chemotherapy chance must be between 0 and 1.")

        cls.set_rates(apoptosis_rate, proliferation_rate, migration_rate)

        cls.RATES['symmetrical_division'] = symmetrical_division_rate
        cls.PROLIFERATION_DECREASE = proliferation_decrease_coef
        cls.DEATH_CHEMOTERAPY_CHANCE = death_chemotherapy_chance

    def proliferation(self, grid):
        """CSC can divide symmetrically or asymmetrically."""
        empty_neighbors = grid.empty_neighbors(self)
        if empty_neighbors:
            new_position = random.choice(empty_neighbors)
            if random.random() <= self.RATES['symmetrical_division']:
                new_cell = StemTumorCell(new_position, self.proliferation_decrease_coef)
            else:
                new_cell = RegularTumorCell(new_position, self.proliferation_decrease_coef)
            grid.add_cell(new_cell)


class ImmuneCell(Cell):
    """Class representing an immune cell."""
    RATES = { 'apoptosis': 0.0, 'proliferation': 0.3, 'migration': 0.0 }
    PROLIFERATION_DECREASE = 0.05
    DEATH_CHEMOTERAPY_CHANCE = 0.02
    DEFAULT_MAX_ATTACKS = 3
    DEFAULT_DEATH_CHANCE = 0.5
    DEFAULT_SUCCESS_CHANCE = 0.5

    def __init__(self, position: tuple[int, int], cell_type: int, proliferation_decrease_coef: float=0.0):
        """Initialize the immune cell with coordinates on a grid."""
        super().__init__(position)
        self.max_attacks = self.DEFAULT_MAX_ATTACKS
        self.attacks_done = 0
        self.age = 0
        self.lifespan = random.randint(10, 30)
        self.cell_type = cell_type
        self.death_chance_of_attack = self.DEFAULT_DEATH_CHANCE
        self.chance_of_succesfull_attack  =  self.DEFAULT_SUCCESS_CHANCE 

    @classmethod
    def set_constants(cls, apoptosis_rate: float,
                    proliferation_rate: float,
                    migration_rate: float,
                    proliferation_decrease_coef: float,
                    death_chemotherapy_chance: float):
        """
        Set the rates for the immune cell.

        Args:
            Summ of rates must be between 0 and 1.
            apoptosis_rate (float): Chance of cell to undergo apoptosis at each step.
            proliferation_rate (float): Chance of cell to proliferate at each step.
            migration_rate (float): Chance of cell to migrate at each step.

            proliferation_decrease_coef (float): Coefficient for decreasing proliferation chance
            after applying chemotherapy, must be between 0 and 1.
            death_chemotherapy_chance (float): Chance of cell death due to chemotherapy,
            must be between 0 and 1.
        """

        if not 0 < (apoptosis_rate+proliferation_rate+migration_rate) <= 1:
            raise ValueError("Rates must sum must be between 0 and 1.")
        if not 0 <= proliferation_decrease_coef <= 1:
            raise ValueError("Proliferation decrease coefficient must be between 0 and 1.")
        if not 0 <= death_chemotherapy_chance <= 1:
            raise ValueError("Death chemotherapy chance must be between 0 and 1.")

        cls.set_rates(apoptosis_rate, proliferation_rate, migration_rate)

        cls.PROLIFERATION_DECREASE = proliferation_decrease_coef
        cls.DEATH_CHEMOTERAPY_CHANCE = death_chemotherapy_chance

    def attack(self, target_cell, grid):
        """Immune cell attacks a tumor cell."""
        neighbors = grid.neighbors(self)
        immune_neighbors = [cell for cell in neighbors if isinstance(cell, ImmuneCell)]
        tumor_neighbors = [cell for cell in neighbors if isinstance(cell, (RegularTumorCell, StemTumorCell))]
        self.attacks_done += 1
        n_I1 = len(immune_neighbors)
        n_PT1 = len(tumor_neighbors)
        if n_PT1 == 0:
            r_I = 0
        else:
           
            r_I =  self.chance_of_succesfull_attack  * (n_I1 / n_PT1)

            if isinstance(target_cell, StemTumorCell):
                r_I *= 0.2
            elif isinstance(target_cell, RegularTumorCell):
                r_I *= 1.0
            if self.cell_type == 0:
                r_I *= 0.8
            elif self.cell_type == 1:
                r_I *= 1.2
        r_I = min(r_I, 1.0)
        

        if random.random() <= r_I:
            if target_cell in grid.cells.values():
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
            
            r_t =  self.death_chance_of_attack  * (n_PT1 / n_I1)
            return min(r_t, 1.0)
    
    def proliferation(self, grid):
        """Immune cell proliferates to an empty neighboring cell after successful kill."""
        empty_neighbors =grid.empty_neighbors(self)
        if not empty_neighbors:
            return
        if random.random() <= self.RATES['proliferation'] : 
            position = random.choice(empty_neighbors)
            new_cell = ImmuneCell(position, cell_type=self.cell_type)
            grid.add_cell(new_cell)


    def make_action(self, grid):
        """Make action for the immune cell based on its type and local context."""
        self.age +=1
        neighbors = grid.neighbors(self)
        tumor_neighbors = [cell for cell in neighbors if isinstance(cell, (RegularTumorCell, StemTumorCell))]

        if tumor_neighbors:
            if self.cell_type == 1:
                for target in tumor_neighbors:
                    if self.attack(target, grid):
                        grid.kill_count += 1
                        self.proliferation(grid)
                        if self.attacks_done >= self.max_attacks:
                            grid.remove_cell(self)
                        return
                    else:
                        grid.failure_count += 1
                        if random.random() <= self.get_failure_death_prob(grid) or self.attacks_done >= self.max_attacks:
                            grid.remove_cell(self)
                            return
            elif self.cell_type == 0:
                # NK — менш агресивні
                target = random.choice(tumor_neighbors)
                if self.attack(target, grid):
                    grid.kill_count += 1
                    self.proliferation(grid)
                    grid.remove_cell(self)
                else:
                    grid.failure_count += 1
                    if random.random() <= self.get_failure_death_prob(grid):
                        grid.remove_cell(self)
        else:
            self.migration(grid)
        if  self.age == self.lifespan:
            if self in grid.cells.values():
                self.apoptosis(grid)

    def apply_immunotherapy(self):
        """Boost immune cell parameters through immunotherapy."""
        self.max_attacks += 2
        self.lifespan += 10
        self.death_chance_of_attack  *= 0.8
        self.chance_of_succesfull_attack *= 3

    def reset_immunotherapy(self):
        """Reset immune cell parameters to their default values."""
        self.max_attacks =  self.DEFAULT_MAX_ATTACKS
       
        self.death_chance_of_attack = self.DEFAULT_DEATH_CHANCE
        self.chance_of_succesfull_attack = self.DEFAULT_SUCCESS_CHANCE