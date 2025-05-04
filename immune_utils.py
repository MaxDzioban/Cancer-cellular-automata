import random
from cells import ImmuneCell, RegularTumorCell, StemTumorCell

def recruit_immune_cells(grid, v, f):
        """
        Recruit new CTL immune cells globally based on successful (v) and failed (f) attacks,
        and the current tumor cell population.
        """
        
        nT = grid.count_cells((RegularTumorCell, StemTumorCell))
        nPT = grid.count_cells(RegularTumorCell)

        if nT == 0:
            return 

        newborns = int((v - f) * (nPT / nT))

        if newborns <= 0:
            return

        empty_cells = grid.empty_cells()
        for _ in range(min(newborns, len(empty_cells))):
            position = random.choice(empty_cells)
            value = random.choice([0, 1])
            new_cell = ImmuneCell(position, cell_type=value)
            grid.add_cell(new_cell)
            empty_cells.remove(position)
