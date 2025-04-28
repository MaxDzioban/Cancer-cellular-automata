"""visualize process of tumor growth"""

from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, 
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
    QGroupBox, QSlider, QSpinBox, QFormLayout, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QPen, QFont

from cells import Cell, RegularTumorCell, StemTumorCell, ImmuneCell
from grid import Grid
import sys
import numpy as np


class TumorGrowthWindow(QMainWindow):
    def __init__(self, grid_size=50, num_steps=100, update_interval=150):
        super().__init__()
        self.setWindowTitle("Tumor Growth Simulation")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #333333;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QGroupBox {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #555555;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #AAAAAA;
                border: 1px solid #777777;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSpinBox {
                background-color: #555555;
                color: white;
                border: 1px solid #777777;
                padding: 2px;
                border-radius: 3px;
            }
        """)

        self.grid_size = grid_size
        self.num_steps = num_steps
        self.current_step = 0
        self.update_interval = update_interval
        self.running = True
        self.edit_mode = None  # 'add', 'remove', or None

        # Set cell size based on grid size initially
        self.cell_size = min(600 // grid_size, 20)

        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel for controls
        left_panel = QVBoxLayout()
        
        # Title
        title_label = QLabel("Tumor Growth Simulation")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(title_label)
        
        # Info group
        info_group = QGroupBox("Info")
        info_layout = QFormLayout()
        self.status_label = QLabel(f"Step: 0, Cells: 0")
        info_layout.addRow("Status:", self.status_label)
        info_group.setLayout(info_layout)
        left_panel.addWidget(info_group)
        
        # Options group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        # Grid size control
        grid_size_layout = QFormLayout()
        self.grid_size_spinbox = QSpinBox()
        self.grid_size_spinbox.setRange(10, 200)
        self.grid_size_spinbox.setValue(grid_size)
        self.grid_size_spinbox.setSingleStep(5)
        grid_size_layout.addRow("Grid Size:", self.grid_size_spinbox)
        options_layout.addLayout(grid_size_layout)
        
        # Speed control
        speed_layout = QFormLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 500)
        self.speed_slider.setValue(update_interval)
        self.speed_slider.setInvertedAppearance(True)  # Lower value = faster speed
        speed_layout.addRow("Speed:", self.speed_slider)
        options_layout.addLayout(speed_layout)
        
        options_group.setLayout(options_layout)
        left_panel.addWidget(options_group)
        
        # Controls group
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        
        self.btn_toggle = QPushButton("Pause")
        self.btn_toggle.clicked.connect(self.toggle_simulation)
        controls_layout.addWidget(self.btn_toggle)
        
        self.btn_regenerate = QPushButton("Regenerate")
        self.btn_regenerate.clicked.connect(self.regenerate)
        controls_layout.addWidget(self.btn_regenerate)
        
        self.btn_add = QPushButton("Add Cell")
        self.btn_add.clicked.connect(lambda: self.set_edit_mode("add"))
        controls_layout.addWidget(self.btn_add)
        
        self.btn_remove = QPushButton("Remove Cell")
        self.btn_remove.clicked.connect(lambda: self.set_edit_mode("remove"))
        controls_layout.addWidget(self.btn_remove)
        
        controls_group.setLayout(controls_layout)
        left_panel.addWidget(controls_group)
        
        # Add stretch to push controls to the top
        left_panel.addStretch()
        
        # Right panel for visualization
        right_panel = QVBoxLayout()
        
        # Create scene and view FIRST (before using them)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setBackgroundBrush(QBrush(QColor("#222222")))
        self.view.setFrameStyle(QFrame.NoFrame)
        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.handle_click
        
        right_panel.addWidget(self.view)

        # Add panels to main layout
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel)
        left_panel_widget.setFixedWidth(250)  # Set fixed width for the left panel
        
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel)
        
        main_layout.addWidget(left_panel_widget)
        main_layout.addWidget(right_panel_widget, 1)  # Give the visualization more space
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Initialize visualization AFTER creating the scene
        self.init_grid(grid_size)
        self.create_visualization()
        
        # Connect signals
        self.grid_size_spinbox.valueChanged.connect(self.update_grid_size)
        self.speed_slider.valueChanged.connect(self.update_speed)
        
        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(self.update_interval)
        
        # Set window size
        self.resize(900, 600)

    def init_grid(self, size):
        """Initialize the grid and cell visualization"""
        # Set cell behavior
        Cell.set_rates(apoptosis=0.01, proliferation=0.3, migration=0.2)
        
        self.grid_size = size
        
        # Calculate cell size based on grid size
        self.cell_size = min(600 // size, 20)  # Max size of 20px, but scale down for larger grids
        
        self.grid = Grid(size, size)
        center = size // 2
        self.initialize_tumor(center, center)

        self.cell_items = [[None for _ in range(size)] for _ in range(size)]

    def update_grid_size(self):
        """Handle grid size change"""
        new_size = self.grid_size_spinbox.value()
        if new_size != self.grid_size:
            # clear everythingf
            self.scene.clear()

            self.init_grid(new_size)

            self.create_visualization()

            self.current_step = 0
            self.update_view()
            self.status_label.setText(f"Step: 0, Cells: {self.grid.num_cells}")

    def create_visualization(self):
        """Create the visual representation of the grid"""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rect = QGraphicsRectItem(j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size)
                cell = self.grid.cells.get((i, j))
                if cell:
                    color = self.get_cell_color(cell)
                else:
                    color = QColor("#FFFFFF")
                rect.setBrush(QBrush(color))
                rect.setPen(QPen(QColor("#333333"), 0.5))
                self.scene.addItem(rect)
                self.cell_items[i][j] = rect

    def update_speed(self):
        """Update the simulation speed"""
        self.update_interval = self.speed_slider.value()
        self.timer.setInterval(self.update_interval)

    def get_cell_color(self, cell):
        """Get the color for a cell based on its type"""
        if isinstance(cell, RegularTumorCell):
            return QColor("#FF5733")  
        elif isinstance(cell, StemTumorCell):
            return QColor("#C70039") 
        elif isinstance(cell, ImmuneCell):
            if cell.cell_type == 0:
                return QColor("#33FF57")
            elif cell.cell_type == 1:
                return QColor("#33C1FF")  
            else:
                return QColor("#00FFFF")
        else:
            return QColor("#000000")

    def set_edit_mode(self, mode):
        """Set the edit mode (add or remove cells)"""
        if self.edit_mode == mode:
            self.edit_mode = None
            self.btn_add.setStyleSheet("") if mode == "add" else self.btn_remove.setStyleSheet("")
        else:
            self.edit_mode = mode
            if mode == "add":
                self.btn_add.setStyleSheet("background-color: #007ACC;")
                self.btn_remove.setStyleSheet("")
            else:
                self.btn_remove.setStyleSheet("background-color: #CC0000;")
                self.btn_add.setStyleSheet("")
        print(f"Edit mode: {self.edit_mode}")

    def toggle_simulation(self):
        """Pause or resume the simulation"""
        self.running = not self.running
        self.btn_toggle.setText("Resume" if not self.running else "Pause")
        self.btn_toggle.setStyleSheet("background-color: #007ACC;" if self.running else "background-color: #CC7A00;")

    def regenerate(self):
        """Clear the grid and reinitialize the tumor"""
        self.grid.empty_grid()
        center = self.grid_size // 2
        self.initialize_tumor(center, center)
        self.current_step = 0
        self.update_view()
        self.status_label.setText(f"Step: 0, Cells: {self.grid.num_cells}")

    def handle_click(self, event):
        pos = self.view.mapToScene(event.pos())
        row = int(pos.y() // self.cell_size)
        col = int(pos.x() // self.cell_size)

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            if self.edit_mode == "add":
                if not self.grid.grid[row, col]:
                    self.grid.add_cell(Cell((row, col)))
                    self.update_view()
            elif self.edit_mode == "remove":
                if self.grid.grid[row, col]:
                    self.grid.remove_cell_at((row, col))
                    self.update_view()

    def initialize_tumor(self, center_x, center_y, initial_radius=3, num_immune=200):
        """Initialize tumor cells in a circular pattern at the center."""
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                distance = np.sqrt((i - center_x) ** 2 + (j - center_y) ** 2)
                if distance <= initial_radius:
                    rand = np.random.random()
                    if rand < 0.5:
                        self.grid.add_cell(RegularTumorCell((i, j)))
                    else:
                        self.grid.add_cell(StemTumorCell((i, j)))

        immune_positions = []
        while len(immune_positions) < num_immune:
            x = np.random.randint(0, 3)  # перші 3 рядки
            y = np.random.randint(0, 3)  # перші 3 стовпці
            if not self.grid.grid[x, y]:
                immune_positions.append((x, y))

        for pos in immune_positions:
            cell_type = np.random.choice([0, 1])
            self.grid.add_cell(ImmuneCell(pos, cell_type))

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
                if 0<=i < len(self.cell_items) and 0<= j < len(self.cell_items[i]) and self.cell_items[i][j] is not None:
                    cell = self.grid.cells.get((i, j))
                    if cell:
                        color = self.get_cell_color(cell)
                    else:
                        color = QColor("#FFFFFF")
                    self.cell_items[i][j].setBrush(QBrush(color))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TumorGrowthWindow(grid_size=50, num_steps=500)
    window.show()
    sys.exit(app.exec_())
