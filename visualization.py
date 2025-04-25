# """visualize process of tumor growth"""
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib import animation
# from matplotlib.colors import ListedColormap
# from cells import Cell
# from grid import Grid

# def initialize_tumor(grid, center_x, center_y, initial_radius=3):
#     """Initialize tumor cells in a circular pattern at the center."""
#     for i in range(grid.rows):
#         for j in range(grid.cols):
#             # Calculate distance from center
#             distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
#             # Create cells within the initial radius
#             if distance <= initial_radius:
#                 cell = Cell((i, j))
#                 grid.add_cell(cell)

# def update(frame_num, grid, img):
#     """Update function for animation."""
#     # Make actions for all cells
#     grid.make_action()
    
#     # Update the grid visualization
#     grid_array = grid.grid.astype(int)
#     img.set_array(grid_array)
    
#     # Add a title with the current frame and cell count
#     plt.title(f"Tumor Growth Simulation - Step: {frame_num}, Cells: {grid.num_cells}")
    
#     return [img]

# def visualize_tumor_growth(grid_size=50, num_frames=100, fps=10):
#     """Create and display animation of tumor growth."""
#     # Set cell behavior rates
#     Cell.set_rates(apoptosis=0.01, proliferation=0.3, migration=0.2)
    
#     # Initialize grid
#     grid = Grid(grid_size, grid_size)
#     center = grid_size // 2
#     initialize_tumor(grid, center, center)
    
#     # Set up the plot
#     fig, ax = plt.subplots(figsize=(8, 8))
#     cmap = ListedColormap(['white', 'red'])
#     img = ax.imshow(grid.grid.astype(int), cmap=cmap, interpolation='nearest')
#     ax.set_xticks([])
#     ax.set_yticks([])
#     plt.title("Tumor Growth Simulation - Step: 0, Cells: {}".format(grid.num_cells))
    
#     # Create the animation
#     anim = animation.FuncAnimation(
#         fig, update, frames=num_frames, fargs=(grid, img),
#         interval=1000//fps, blit=True
#     )
    
#     # Display or save the animation
#     plt.tight_layout()
    
#     # To save as MP4 file (requires ffmpeg):
#     # anim.save('tumor_growth.mp4', fps=fps, extra_args=['-vcodec', 'libx264'])
#     anim.save('tumor_growth.gif', writer='pillow', fps=fps)
#     # plt.show()
    
#     return anim

# if __name__ == "__main__":
#     # Run the visualization with default parameters
#     visualize_tumor_growth(grid_size=50, num_frames=30, fps=15)



from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, 
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QPen

from cells import Cell
from grid import Grid
import sys
import numpy as np


class TumorGrowthWindow(QMainWindow):
    def __init__(self, grid_size=50, num_steps=100, update_interval=150):
        super().__init__()
        self.setWindowTitle("Tumor Growth Simulation")

        self.grid_size = grid_size
        self.num_steps = num_steps
        self.current_step = 0
        self.update_interval = update_interval
        self.running = True
        self.edit_mode = None  # 'add', 'remove', or None

        # Set cell behavior
        Cell.set_rates(apoptosis=0.01, proliferation=0.3, migration=0.2)

        self.grid = Grid(grid_size, grid_size)
        center = grid_size // 2
        self.initialize_tumor(center, center)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.handle_click

        self.cell_size = 10
        self.cell_items = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        for i in range(grid_size):
            for j in range(grid_size):
                rect = QGraphicsRectItem(j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(Qt.white))
                rect.setPen(QPen(Qt.NoPen))
                self.scene.addItem(rect)
                self.cell_items[i][j] = rect

        self.status_label = QLabel(f"Step: 0, Cells: {self.grid.num_cells}")

        # Buttons
        self.btn_add = QPushButton("Add Cell")
        self.btn_remove = QPushButton("Remove Cell")
        self.btn_toggle = QPushButton("Pause")

        self.btn_add.clicked.connect(lambda: self.set_edit_mode("add"))
        self.btn_remove.clicked.connect(lambda: self.set_edit_mode("remove"))
        self.btn_toggle.clicked.connect(self.toggle_simulation)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_add)
        buttons_layout.addWidget(self.btn_remove)
        buttons_layout.addWidget(self.btn_toggle)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(self.update_interval)

    def set_edit_mode(self, mode):
        self.edit_mode = mode if self.edit_mode != mode else None
        print(f"Edit mode: {self.edit_mode}")

    def toggle_simulation(self):
        self.running = not self.running
        self.btn_toggle.setText("Resume" if not self.running else "Pause")

    def handle_click(self, event):
        pos = self.view.mapToScene(event.pos())
        row = int(pos.y() // self.cell_size)
        col = int(pos.x() // self.cell_size)

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            if self.edit_mode == "add":
                if self.grid.grid[row, col] == 0:
                    self.grid.add_cell(Cell((row, col)))
            elif self.edit_mode == "remove":
                if self.grid.grid[row, col] == 1:
                    self.grid.remove_cell_at((row, col))

            self.update_view()

    def initialize_tumor(self, center_x, center_y, initial_radius=3):
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                distance = np.sqrt((i - center_x) ** 2 + (j - center_y) ** 2)
                if distance <= initial_radius:
                    self.grid.add_cell(Cell((i, j)))

    def update_simulation(self):
        if not self.running or self.current_step >= self.num_steps:
            return

        self.grid.make_action()
        self.current_step += 1
        self.update_view()
        self.status_label.setText(f"Step: {self.current_step}, Cells: {self.grid.num_cells}")

    def update_view(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                color = QColor("red") if self.grid.grid[i, j] == 1 else QColor("white")
                self.cell_items[i][j].setBrush(QBrush(color))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TumorGrowthWindow(grid_size=50, num_steps=200)
    window.show()
    sys.exit(app.exec_())
