"""visualize process of tumor growth"""
import sys

from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, 
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
    QGroupBox, QSlider, QSpinBox, QFormLayout, QFrame, QSizePolicy,
    QMessageBox, QFileDialog, QInputDialog, QDoubleSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QPen, QFont
import json
from cells import Cell
from cells import Cell, RegularTumorCell, StemTumorCell, ImmuneCell
from grid import Grid
import numpy as np
import random
from cell_editor import CellEditor

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

        self.edit_mode = None
        # 'add', 'remove', or None
        
        self.grid_line_width = 0.5
        # початкова товщина меж клітин
        
        self.custom_cell_templates = {}
        # для зберігання кастомних клітин із JSON

        # Set cell size based on grid size initially
        self.cell_size = min(600 // grid_size, 20)

        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel for controls
        left_panel = QVBoxLayout()
        
        # Title
        title_label = QLabel("Tumor Growth Simulation")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(title_label)
        
        # Info group
        info_group = QGroupBox("Info")
        info_layout = QFormLayout()
        self.status_label = QLabel(f"Step: 0, Cells: 0")
        info_layout.addRow("Status:", self.status_label)
        info_group.setLayout(info_layout)
        left_panel.addWidget(info_group)
        
        # Cell Counts group
        counts_group = QGroupBox("Cell Counts")
        counts_layout = QFormLayout()
        self.counts_layout = counts_layout  # доступ з update_cell_counts

        self.regular_tumor_count = QLabel("0")
        self.stem_tumor_count = QLabel("0")
        self.immune_type0_count = QLabel("0")
        self.immune_type1_count = QLabel("0")
        # self.generic_count = QLabel("0")

        # name -> QLabel
        self.custom_cell_labels = {}
        
        counts_layout.addRow("Regular Tumor Cells:", self.regular_tumor_count)
        counts_layout.addRow("Stem Tumor Cells:", self.stem_tumor_count)
        counts_layout.addRow("Immune Cells (Type 0):", self.immune_type0_count)
        counts_layout.addRow("Immune Cells (Type 1):", self.immune_type1_count)
        # counts_layout.addRow("Generic Cells:", self.generic_count)
        
        counts_group.setLayout(counts_layout)
        left_panel.addWidget(counts_group)
        
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
        
        # Initial counts control
        initial_counts_layout = QFormLayout()
        
        self.initial_tumor_radius = QSpinBox()
        self.initial_tumor_radius.setRange(1, 10)
        self.initial_tumor_radius.setValue(3)
        self.initial_tumor_radius.setSingleStep(1)
        initial_counts_layout.addRow("Initial Tumor Radius:", self.initial_tumor_radius)
        
        self.initial_immune_count = QSpinBox()
        self.initial_immune_count.setRange(0, 1000)
        self.initial_immune_count.setValue(200)
        self.initial_immune_count.setSingleStep(50)
        initial_counts_layout.addRow("Initial Immune Cells:", self.initial_immune_count)
        options_layout.addLayout(initial_counts_layout)
        options_group.setLayout(options_layout)
        left_panel.addWidget(options_group)

        # Grid line width control
        line_width_layout = QFormLayout()
        self.line_width_slider = QSlider(Qt.Horizontal)
        self.line_width_slider.setRange(0, 10)
        self.line_width_slider.setValue(int(self.grid_line_width * 10))
        self.line_width_slider.valueChanged.connect(self.update_line_thickness)
        line_width_layout.addRow("Line Thickness:", self.line_width_slider)
        options_layout.addLayout(line_width_layout)

        # Controls group
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()

        self.btn_load_ai_cell = QPushButton("Load Cell (JSON)")
        self.btn_load_ai_cell.clicked.connect(self.load_ai_cell)
        controls_layout.addWidget(self.btn_load_ai_cell)


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
        



################################ Regular Tumor Cell Parameters ##############################################################
        # Regular Tumor Cell Parameters on the right
        global_params_layout = QVBoxLayout()
        rtc_group = QGroupBox("Regular Cancer Cell Parameters")
        rtc_form = QFormLayout()
        # cпінбокси
        self.rtc_apoptosis = QDoubleSpinBox()
        self.rtc_apoptosis.setRange(0.01, 1)
        self.rtc_apoptosis.setSingleStep(0.01)
        # self.rtc_apoptosis.setValue(Cell.RATES['apoptosis'])

        self.rtc_proliferation = QDoubleSpinBox()
        self.rtc_proliferation.setRange(0.01, 1)
        self.rtc_proliferation.setSingleStep(0.01)
        # self.rtc_proliferation.setValue(Cell.RATES['proliferation'])

        self.rtc_migration = QDoubleSpinBox()
        self.rtc_migration.setRange(0.01, 1)
        self.rtc_migration.setSingleStep(0.01)
        # self.rtc_migration.setValue(Cell.RATES['migration'])

        self.rtc_max_divisions = QSpinBox()
        self.rtc_max_divisions.setRange(1, 999)
        self.rtc_max_divisions.setSingleStep(1)

        self.rtc_prolif_decrease = QDoubleSpinBox()
        self.rtc_prolif_decrease.setRange(0.01, 1)
        self.rtc_prolif_decrease.setSingleStep(0.01)
        self.rtc_prolif_decrease.setValue(Cell.PROLIFERATION_DECREASE)

        self.rtc_chemo_chance = QDoubleSpinBox()
        self.rtc_chemo_chance.setRange(0.01, 1)
        self.rtc_chemo_chance.setSingleStep(0.01)
        self.rtc_chemo_chance.setValue(Cell.DEATH_CHEMOTHERAPY_CHANCE)
        # поля у форму
        rtc_form.addRow("Apoptosis:", self.rtc_apoptosis)
        rtc_form.addRow("Proliferation:", self.rtc_proliferation)
        rtc_form.addRow("Migration:", self.rtc_migration)
        rtc_form.addRow("Max num of divisions:", self.rtc_max_divisions)
        rtc_form.addRow("Prolif. ↓ for chemo:", self.rtc_prolif_decrease)
        rtc_form.addRow("Chemo death chance:", self.rtc_chemo_chance)
        # Після створення спінбоксів:
        # global_apoptosis.editingFinished.connect(self.apply_global_cell_parameters)
        self.rtc_apoptosis.editingFinished.connect(self.apply_cell_parameters)
        self.rtc_proliferation.editingFinished.connect(self.apply_cell_parameters)
        self.rtc_migration.editingFinished.connect(self.apply_cell_parameters)
        self.rtc_max_divisions.editingFinished.connect(self.apply_cell_parameters)
        self.rtc_prolif_decrease.editingFinished.connect(self.apply_cell_parameters)
        self.rtc_chemo_chance.editingFinished.connect(self.apply_cell_parameters)

        rtc_group.setLayout(rtc_form)
        global_params_layout.addWidget(rtc_group)




################################ Stem Tumor Cell Parameters ##############################################################
        # Regular Tumor Cell Parameters on the right
        stc_group = QGroupBox("Stem Cell Parameters")
        stc_form = QFormLayout()
        # cпінбокси
        self.stc_apoptosis = QDoubleSpinBox()
        self.stc_apoptosis.setRange(0.01, 1)
        self.stc_apoptosis.setSingleStep(0.01)
        # self.stc_apoptosis.setValue(Cell.RATES['apoptosis'])

        self.stc_proliferation = QDoubleSpinBox()
        self.stc_proliferation.setRange(0.01, 1)
        self.stc_proliferation.setSingleStep(0.01)
        # self.stc_proliferation.setValue(Cell.RATES['proliferation'])

        self.stc_migration = QDoubleSpinBox()
        self.stc_migration.setRange(0.01, 1)
        self.stc_migration.setSingleStep(0.01)
        # self.stc_migration.setValue(Cell.RATES['migration'])

        self.stc_sym_division = QDoubleSpinBox()
        self.stc_sym_division.setRange(0.01, 1)
        self.stc_sym_division.setSingleStep(0.01)

        self.stc_prolif_decrease = QDoubleSpinBox()
        self.stc_prolif_decrease.setRange(0.01, 1)
        self.stc_prolif_decrease.setSingleStep(0.01)
        # self.stc_prolif_decrease.setValue(Cell.PROLIFERATION_DECREASE)

        self.stc_chemo_chance = QDoubleSpinBox()
        self.stc_chemo_chance.setRange(0.01, 1)
        self.stc_chemo_chance.setSingleStep(0.01)
        # self.stc_chemo_chance.setValue(Cell.DEATH_CHEMOTHERAPY_CHANCE)

        stc_form.addRow("Apoptosis:", self.stc_apoptosis)
        stc_form.addRow("Proliferation:", self.stc_proliferation)
        stc_form.addRow("Migration:", self.stc_migration)
        stc_form.addRow("Symm division:", self.stc_sym_division)
        stc_form.addRow("Prolif. ↓ for chemo:", self.stc_prolif_decrease)
        stc_form.addRow("Chemo death chance:", self.stc_chemo_chance)

        self.stc_apoptosis.editingFinished.connect(self.apply_cell_parameters)
        self.stc_proliferation.editingFinished.connect(self.apply_cell_parameters)
        self.stc_migration.editingFinished.connect(self.apply_cell_parameters)
        self.stc_sym_division.editingFinished.connect(self.apply_cell_parameters)
        self.stc_prolif_decrease.editingFinished.connect(self.apply_cell_parameters)
        self.stc_chemo_chance.editingFinished.connect(self.apply_cell_parameters)

        stc_group.setLayout(stc_form)
        global_params_layout.addWidget(stc_group)



################################ Immune Cell Parameters ##############################################################
        im_group = QGroupBox("Immune Cell Parameters")
        im_form = QFormLayout()

        # Immune Cell Parameters
        self.im_apoptosis = QDoubleSpinBox()
        self.im_apoptosis.setRange(0, 1)
        self.im_apoptosis.setSingleStep(0.01)
        # self.im_apoptosis.setValue(ImmuneCell.RATES['apoptosis'])

        self.im_proliferation = QDoubleSpinBox()
        self.im_proliferation.setRange(0, 1)
        self.im_proliferation.setSingleStep(0.01)
        # self.im_proliferation.setValue(ImmuneCell.RATES['proliferation'])

        self.im_migration = QDoubleSpinBox()
        self.im_migration.setRange(0, 1)
        self.im_migration.setSingleStep(0.01)
        # self.im_migration.setValue(ImmuneCell.RATES['migration'])

        self.im_prolif_decrease = QDoubleSpinBox()
        self.im_prolif_decrease.setRange(0.01, 1)
        self.im_prolif_decrease.setSingleStep(0.01)
        # self.im_prolif_decrease.setValue(Cell.PROLIFERATION_DECREASE)

        self.im_chemo_chance = QDoubleSpinBox()
        self.im_chemo_chance.setRange(0.01, 1)
        self.im_chemo_chance.setSingleStep(0.01)
        # self.im_chemo_chance.setValue(Cell.DEATH_CHEMOTHERAPY_CHANCE)

        im_form.addRow("Apoptosis:", self.im_apoptosis)
        im_form.addRow("Proliferation:", self.im_proliferation)
        im_form.addRow("Migration:", self.im_migration)
        im_form.addRow("Prolif. ↓ for chemo:", self.im_prolif_decrease)
        im_form.addRow("Chemo death chance:", self.im_chemo_chance)

        self.im_apoptosis.editingFinished.connect(self.apply_cell_parameters)
        self.im_proliferation.editingFinished.connect(self.apply_cell_parameters)
        self.im_migration.editingFinished.connect(self.apply_cell_parameters)
        self.im_prolif_decrease.editingFinished.connect(self.apply_cell_parameters)
        self.im_chemo_chance.editingFinished.connect(self.apply_cell_parameters)

        im_group.setLayout(im_form)
        global_params_layout.addWidget(im_group)


################################ Chemotherapy ##############################################################
        chemo_group = QGroupBox("Хіміотерапія")
        chemo_layout = QVBoxLayout()
        # для ручного запуску хіміотерапії
        self.btn_apply_chemo = QPushButton("Застосувати хіміотерапію")
        self.btn_apply_chemo.clicked.connect(self.apply_chemo_once)
        chemo_layout.addWidget(self.btn_apply_chemo)
        # застосування кожні N кроків
        self.chemo_every_n_checkbox = QCheckBox("Автоматично кожні N кроків")
        chemo_layout.addWidget(self.chemo_every_n_checkbox)
        self.chemo_interval_spinbox = QSpinBox()
        self.chemo_interval_spinbox.setRange(1, 10000)
        self.chemo_interval_spinbox.setValue(50)
        chemo_layout.addWidget(QLabel("Інтервал N:"))
        chemo_layout.addWidget(self.chemo_interval_spinbox)

        chemo_group.setLayout(chemo_layout)
        global_params_layout.addWidget(chemo_group)
        global_params_layout.addStretch()




        global_params_widget = QWidget()
        global_params_widget.setLayout(global_params_layout)
        global_params_widget.setFixedWidth(250)
        
        main_layout.addWidget(left_panel_widget)
        main_layout.addWidget(right_panel_widget, 1)
        main_layout.addWidget(global_params_widget)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.init_grid(self.grid_size)
        self.create_visualization()
        self.grid_size_spinbox.valueChanged.connect(self.update_grid_size)
        self.speed_slider.valueChanged.connect(self.update_speed)
        self.initial_tumor_radius.valueChanged.connect(self.update_initial_settings)
        self.initial_immune_count.valueChanged.connect(self.update_initial_settings)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(self.update_interval)
        self.initialize_default_parameters()
        self.resize(900, 600)



    def init_grid(self, size):
        """Initialize the grid and cell visualization"""

        self.grid_size = size
        self.cell_size = min(600 // size, 20)
        
        self.grid = Grid(size, size)
        center = size // 2
        self.initialize_tumor(center, center)

        self.cell_items = [[None for _ in range(size)] for _ in range(size)]

    def update_grid_size(self):
        """Handle grid size change"""
        new_size = self.grid_size_spinbox.value()
        if new_size != self.grid_size:
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
                rect.setAcceptHoverEvents(True)
                cell = self.grid.cells.get((i, j))
                if cell:
                    color = self.get_cell_color(cell)
                else:
                    color = QColor("#FFFFFF")
                rect.setBrush(QBrush(color))
                # rect.setPen(QPen(QColor("#333333"), 0.5))
                rect.setPen(QPen(QColor("#333333"), self.grid_line_width))
                self.scene.addItem(rect)
                self.cell_items[i][j] = rect

    def update_speed(self):
        """Update the simulation speed"""
        self.update_interval = self.speed_slider.value()
        self.timer.setInterval(self.update_interval)

    def get_cell_color(self, cell):
        """Get the color for a cell based on its type or JSON-defined color"""
        if hasattr(cell, "color"):
            return QColor(*cell.color)
        
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
        if mode == "add":
            items = ["Regular Tumor", "Stem Tumor", "Immune (Type 0)", "Immune (Type 1)", "Load from JSON"]
            items += list(self.custom_cell_templates.keys())
            item, ok = QInputDialog.getItem(self, "Choose Cell Type", "Cell type to add:", items, 0, False)
            if not ok:
                self.edit_mode = None
                self.selected_cell_type = None
                return

            if item == "Load from JSON":
                file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON Cell", "", "JSON Files (*.json)")
                if not file_path:
                    return

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    name = data.get("name", "Unnamed")
                    cell_type = 0 if data["behavior"].get("attacks") else 1

                    self.custom_cell_templates[name] = {
                        "color": tuple(data.get("color", [0, 255, 0])),
                        "cell_type": cell_type,
                        "energy": data.get("energy", 50),
                        "attack_power": data.get("attack_power", 10),
                        "defense": data.get("defense", 5),
                        "behavior": data.get("behavior", {"moves": True, "attacks": True, "heals": False})
                    }

                    self.selected_cell_type = name
                    self.edit_mode = "add"
                    self.btn_add.setStyleSheet("background-color: #007ACC;")
                    self.btn_remove.setStyleSheet("")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load JSON: {e}")
                    return
            else:
                self.selected_cell_type = item
                self.edit_mode = "add"
                self.btn_add.setStyleSheet("background-color: #007ACC;")
                self.btn_remove.setStyleSheet("")
        elif mode == "remove":
            self.edit_mode = "remove"
            self.selected_cell_type = None
            self.btn_remove.setStyleSheet("background-color: #CC0000;")
            self.btn_add.setStyleSheet("")
        else:
            self.edit_mode = None
            self.selected_cell_type = None
            self.btn_add.setStyleSheet("")
            self.btn_remove.setStyleSheet("")


    def toggle_simulation(self):
        """Pause or resume the simulation"""
        self.running = not self.running
        self.btn_toggle.setText("Resume" if not self.running else "Pause")
        self.btn_toggle.setStyleSheet("background-color: #007ACC;" if self.running else "background-color: #CC7A00;")

    def update_initial_settings(self):
        """Update initial settings without regenerating immediately"""
        # Settings are applied when regenerate is clicked
        pass
    
    def update_line_thickness(self):
        """Оновити товщину меж клітинок."""
        self.grid_line_width = self.line_width_slider.value() / 10.0
        self.update_view()

    def regenerate(self):
        self.scene.clear()
        # очистити стару

        new_size = self.grid_size_spinbox.value()
        self.init_grid(new_size)
        self.create_visualization()
        self.current_step = 0
        self.update_view()
        self.update_cell_counts()
        self.status_label.setText(f"Step: 0, Cells: {self.grid.num_cells}")

        self.running = False
        self.btn_toggle.setText("Resume")
        self.btn_toggle.setStyleSheet("background-color: #CC7A00;")

    def handle_click(self, event):
        pos = self.view.mapToScene(event.pos())
        row = int(pos.y() // self.cell_size)
        col = int(pos.x() // self.cell_size)

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            if event.button() == Qt.RightButton:
                self.show_cell_info((row, col))
            elif self.edit_mode == "add":
                if not self.grid.grid[row, col]:
                    standard_options = ["Generic", "Regular Tumor", "Stem Tumor", "Immune (Type 0)", "Immune (Type 1)"]
                    custom_options = list(self.custom_cell_templates.keys())
                    all_options = standard_options + custom_options
                    cell_type, ok = QInputDialog.getItem(self, "Select Cell Type", "Choose cell type to add:", all_options, 0, False)
                    if ok:
                        pos = (row, col)
                        cell = None
                        if cell_type == "Generic":
                            cell = Cell(pos)
                        elif cell_type == "Regular Tumor":
                            cell = RegularTumorCell(pos)
                        elif cell_type == "Stem Tumor":
                            cell = StemTumorCell(pos)
                        elif cell_type == "Immune (Type 0)":
                            cell = ImmuneCell(pos, cell_type=0)
                        elif cell_type == "Immune (Type 1)":
                            cell = ImmuneCell(pos, cell_type=1)
                        elif cell_type in custom_options:
                            template = self.custom_cell_templates[cell_type]
                            cell = ImmuneCell(pos, cell_type=template["cell_type"])
                            cell.name = cell_type
                            cell.color = template["color"]
                            rates = template.get("rates", {})
                            cell.rates = {
                                "apoptosis": rates.get("apoptosis", 0.1),
                                "proliferation": rates.get("proliferation", 0.1),
                                "migration": rates.get("migration", 0.1),
                            }
                    if cell:
                        self.grid.add_cell(cell)
                        self.update_view()
            elif self.edit_mode == "remove":
                if self.grid.grid[row, col]:
                    self.grid.remove_cell_at((row, col))
                    self.update_view()

    def initialize_tumor(self, center_x, center_y, initial_radius=3, num_NK_cells=10, num_CTL_cells=10):
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

        corners = [(0, 0), (0, self.grid_size - 1), (self.grid_size - 1, 0), (self.grid_size - 1, self.grid_size - 1)]
        edges = [(0, y) for y in range(1, self.grid_size - 1)] + \
                [(self.grid_size - 1, y) for y in range(1, self.grid_size - 1)] + \
                [(x, 0) for x in range(1, self.grid_size - 1)] + \
                [(x, self.grid_size - 1) for x in range(1, self.grid_size - 1)]
        all_positions = corners + edges
        num_positions = len(all_positions)

        nk_per_position = num_NK_cells // num_positions
        ctl_per_position = num_CTL_cells // num_positions
        nk_remainder = num_NK_cells % num_positions
        ctl_remainder = num_CTL_cells % num_positions

        positions = []
        for i, pos in enumerate(all_positions):
            for _ in range(nk_per_position + (1 if i < nk_remainder else 0)):
                positions.append((pos, 0))  # 0 для NK-клітин
            for _ in range(ctl_per_position + (1 if i < ctl_remainder else 0)):
                positions.append((pos, 1))  # 1 для CTL-клітин

        random.shuffle(positions)

        for pos, cell_type in positions:
            if not self.grid.grid[pos[0], pos[1]]:
                self.grid.add_cell(ImmuneCell(pos, cell_type))


    def update_simulation(self):
        if self.chemo_every_n_checkbox.isChecked():
            interval = self.chemo_interval_spinbox.value()
            if self.current_step % interval == 0:
                self.grid.apply_chemotherapy()

        if not self.running or self.current_step >= self.num_steps:
            return

        self.grid.make_action()
        self.current_step += 1
        self.update_view()
        self.update_cell_counts()
        self.status_label.setText(f"Step: {self.current_step}, Cells: {self.grid.num_cells}")

    def apply_chemo_once(self):
        """Apply chemotherapy manually."""
        self.grid.apply_chemotherapy()
        self.update_view()
        QMessageBox.information(self, "Хіміотерапія", "Хіміотерапію застосовано.")


    def update_cell_counts(self):
        """Update cell count labels with current counts"""
        custom_counts = {}

        # Count each cell type
        regular_tumor = 0
        stem_tumor = 0
        immune_type0 = 0
        immune_type1 = 0
        generic = 0

        for cell in self.grid.cells.values():
            if isinstance(cell, RegularTumorCell):
                regular_tumor += 1
            elif isinstance(cell, StemTumorCell):
                stem_tumor += 1
            elif isinstance(cell, ImmuneCell):
                if cell.cell_type == 0:
                    immune_type0 += 1
                elif cell.cell_type == 1:
                    immune_type1 += 1
            else:
                generic += 1

            # кастомні клітини за іменем
            if hasattr(cell, "name"):
                name = cell.name
                custom_counts[name] = custom_counts.get(name, 0) + 1

        for name, count in custom_counts.items():
            if name not in self.custom_cell_labels:
                label = QLabel("0")
                self.custom_cell_labels[name] = label
                self.counts_layout.addRow(f"{name}:", label)
            self.custom_cell_labels[name].setText(str(count))
        self.regular_tumor_count.setText(str(regular_tumor))
        self.stem_tumor_count.setText(str(stem_tumor))
        self.immune_type0_count.setText(str(immune_type0))
        self.immune_type1_count.setText(str(immune_type1))
        # self.generic_count.setText(str(generic))

        for name, count in custom_counts.items():
            if name not in self.custom_cell_labels:
                label = QLabel("0")
                self.custom_cell_labels[name] = label
                self.counts_layout.addRow(f"{name}:", label)

            label = self.custom_cell_labels[name]
            label.setText(str(count))

            # оновлюй колір
            for cell in self.grid.cells.values():
                if hasattr(cell, "name") and cell.name == name and hasattr(cell, "color"):
                    color = cell.color
                    label.setStyleSheet(f"color: rgb({color[0]}, {color[1]}, {color[2]});")
                    break


    def update_view(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if 0<=i < len(self.cell_items) and 0<= j < len(self.cell_items[i]) and self.cell_items[i][j] is not None:
                    cell = self.grid.cells.get((i, j))
                    if cell:
                        color = self.get_cell_color(cell)
                        tooltip = ""
                        if hasattr(cell, "rates") and isinstance(cell.rates, dict):
                            tooltip = (
                                f"A: {cell.rates.get('apoptosis', 0):.2f}, "
                                f"P: {cell.rates.get('proliferation', 0):.2f}, "
                                f"M: {cell.rates.get('migration', 0):.2f}"
                            )
                        self.cell_items[i][j].setToolTip(tooltip)
                    else:
                        color = QColor("#FFFFFF")
                    self.cell_items[i][j].setBrush(QBrush(color))
                    self.cell_items[i][j].setPen(QPen(QColor("#333333"), self.grid_line_width))
        self.update_cell_counts()

    def load_ai_cell(self):
        """Load a cell from a JSON file and save its template for future placement"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Cell (JSON)", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON: {e}")
            return

        try:
            name = data.get("name", "Unnamed")
            cell_type = 0 if data.get("type") == "immune" else 1

            self.custom_cell_templates[name] = {
                "color": tuple(data.get("color", [0, 255, 0])),
                "cell_type": cell_type,
                "rates": data.get("rates", {"apoptosis": 0.1, "proliferation": 0.1, "migration": 0.1})
            }

            msg = QMessageBox(self)
            msg.setStyleSheet("QLabel{ color: black; }")
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setText(f"Custom cell '{name}' loaded and available in Add Cell menu.")
            msg.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse cell: {e}")


    def show_cell_info(self, position):
        cell = self.grid.cells.get(position)
        if not cell:
            QMessageBox.information(self, "Cell Info", "No cell at this position.")
            return
        info_lines = [f"Position: {cell.position}", f"Class: {cell.__class__.__name__}"]
        for key, value in cell.__dict__.items():
            info_lines.append(f"{key}: {value}")
        cls = cell.__class__
        class_attrs = ['RATES', 'PROLIFERATION_DECREASE', 'DEATH_CHEMOTHERAPY_CHANCE', 'MAX_DIVISIONS']
        for attr in class_attrs:
            if hasattr(cls, attr):
                value = getattr(cls, attr)
                info_lines.append(f"{attr}: {value}")
        info_text = "\n".join(info_lines)
        msg = QMessageBox(self)
        msg.setWindowTitle("Cell Info")
        msg.setTextInteractionFlags(Qt.TextSelectableByMouse)
        msg.setStyleSheet("QLabel { color: black; }")
        msg.setText(info_text)
        msg.exec_()

    def initialize_default_parameters(self):
        """Set default parameters for all cell types"""
        # Default tumor cell parameters
        rtc_apop = 0.1
        rtc_prolif = 0.2
        rtc_mig = 0.05

        # Default stem cell parameters
        stc_apop = 0.05
        stc_prolif = 0.2
        stc_mig = 0.05

        # Default immune cell parameters
        immune_apop = 0.05
        immune_prolif = 0.1
        immune_mig = 0.3

        # Other parameters
        max_divisions = 5
        sym_division_rate = 0.08
        prolif_decrease = 0.05
        chemo_chance = 0.02

        # Apply to cell classes
        RegularTumorCell.set_constants(
            apoptosis_rate=rtc_apop,
            proliferation_rate=rtc_prolif,
            migration_rate=rtc_mig,
            max_divisions=max_divisions,
            proliferation_decrease_coef=prolif_decrease,
            death_chemotherapy_chance=chemo_chance
        )

        StemTumorCell.set_constants(
            apoptosis_rate=stc_apop,
            proliferation_rate=stc_prolif,
            migration_rate=stc_mig,
            symmetrical_division_rate=sym_division_rate,
            proliferation_decrease_coef=prolif_decrease,
            death_chemotherapy_chance=chemo_chance
        )

        ImmuneCell.set_constants(
            apoptosis_rate=immune_apop,
            proliferation_rate=immune_prolif,
            migration_rate=immune_mig,
            proliferation_decrease_coef=prolif_decrease,
            death_chemotherapy_chance=chemo_chance
        )

        # Regular Tumor Cell UI elements
        self.rtc_apoptosis.setValue(rtc_apop)
        self.rtc_proliferation.setValue(rtc_prolif)
        self.rtc_migration.setValue(rtc_mig)
        self.rtc_max_divisions.setValue(max_divisions)
        self.rtc_prolif_decrease.setValue(prolif_decrease)
        self.rtc_chemo_chance.setValue(chemo_chance)

        # Stem Tumor Cell UI elements
        self.stc_apoptosis.setValue(stc_apop)
        self.stc_proliferation.setValue(stc_prolif)
        self.stc_migration.setValue(stc_mig)
        self.stc_sym_division.setValue(sym_division_rate)
        self.stc_prolif_decrease.setValue(prolif_decrease)
        self.stc_chemo_chance.setValue(chemo_chance)

        # Immune Cell UI elements
        self.im_apoptosis.setValue(immune_apop)
        self.im_proliferation.setValue(immune_prolif)
        self.im_migration.setValue(immune_mig)
        self.im_prolif_decrease.setValue(prolif_decrease)
        self.im_chemo_chance.setValue(chemo_chance)

    def apply_cell_parameters(self):
        """Apply parameters to the all cell type"""
        # Get RTC parameters
        rtc_apop = self.rtc_apoptosis.value()
        rtc_prolif = self.rtc_proliferation.value()
        rtc_mig = self.rtc_migration.value()
        rtc_max_divisions = self.rtc_max_divisions.value()
        rtc_prolif_decrease = self.rtc_prolif_decrease.value()
        rtc_chemo_chance = self.rtc_chemo_chance.value()

        # Get STC parameters
        stc_apop = self.stc_apoptosis.value()
        stc_prolif = self.stc_proliferation.value()
        stc_mig = self.stc_migration.value()
        stc_sym_division = self.stc_sym_division.value()
        stc_prolif_decrease = self.stc_prolif_decrease.value()
        stc_chemo_chance = self.stc_chemo_chance.value()

        # Get immune parameters
        i_apop = self.im_apoptosis.value()
        i_prolif = self.im_proliferation.value()
        i_mig = self.im_migration.value()
        i_prolif_decrease = self.im_prolif_decrease.value()
        i_chemo_chance = self.im_chemo_chance.value()

        rtc_total = round(rtc_apop + rtc_prolif + rtc_mig, 6)
        stc_total = round(stc_apop + stc_prolif + stc_mig, 6)
        immune_total = round(i_apop + i_prolif + i_mig, 6)

        # Parameter validation
        if not 0 < rtc_total <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Sum of Regular Tumor Cell parameters must be between 0 and 1.")
            return

        if not 0 < stc_total <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Sum of Stem Tumor Cell parameters must be between 0 and 1.")
            return

        if not 0 < immune_total <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Sum of Immune Cell parameters must be between 0 and 1.")
            return

        if rtc_max_divisions < 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Maximum divisions must be at least 1.")
            return

        if not 0 < rtc_prolif_decrease <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Proliferation decrease coefficient must be between 0 and 1.")
            return

        if not 0 < rtc_chemo_chance <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Chemotherapy death chance must be between 0 and 1.")
            return

        if not 0 < stc_sym_division <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Symmetrical division rate must be between 0 and 1.")
            return

        if not 0 < stc_prolif_decrease <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Proliferation decrease coefficient must be between 0 and 1.")
            return

        if not 0 < stc_chemo_chance <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Chemotherapy death chance must be between 0 and 1.")
            return

        if not 0 < i_prolif_decrease <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Proliferation decrease coefficient must be between 0 and 1.")
            return

        if not 0 < i_chemo_chance <= 1:
            QMessageBox.critical(self, "Invalid Parameters",
                            "Chemotherapy death chance must be between 0 and 1.")
            return


        # Apply parameters to each cell type
        RegularTumorCell.set_constants(
            apoptosis_rate=rtc_apop,
            proliferation_rate=rtc_prolif,
            migration_rate=rtc_mig,
            max_divisions=rtc_max_divisions,
            proliferation_decrease_coef=rtc_prolif_decrease,
            death_chemotherapy_chance=rtc_chemo_chance
        )

        StemTumorCell.set_constants(
            apoptosis_rate=stc_apop,
            proliferation_rate=stc_prolif,
            migration_rate=stc_mig,
            symmetrical_division_rate=stc_sym_division,
            proliferation_decrease_coef=stc_prolif_decrease,
            death_chemotherapy_chance=stc_chemo_chance
        )

        ImmuneCell.set_constants(
            apoptosis_rate=i_apop,
            proliferation_rate=i_prolif,
            migration_rate=i_mig,
            proliferation_decrease_coef=i_prolif_decrease,
            death_chemotherapy_chance=i_chemo_chance
        )


class MainMenu(QMainWindow):
    def __init__(self, api_key):
        super().__init__()
        self.setWindowTitle("Імунна симуляція - Головне меню")
        self.setFixedSize(300, 200)

        central_widget = QWidget()
        layout = QVBoxLayout()

        sim_button = QPushButton("Запустити симуляцію")
        sim_button.clicked.connect(self.open_simulation)

        cell_button = QPushButton("Редактор клітин (AI)")
        cell_button.clicked.connect(lambda: self.open_cell_editor(api_key))

        layout.addWidget(sim_button)
        layout.addWidget(cell_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_simulation(self):
        self.sim_window = TumorGrowthWindow(grid_size=50, num_steps=100000)
        self.sim_window.show()

    def open_cell_editor(self, api_key):
        self.cell_editor = CellEditor(api_key)
        self.cell_editor.show()
