import json
import openai
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QMessageBox
)

class CellEditor(QWidget):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Додати нову клітину")
        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Назва клітини")
        layout.addWidget(QLabel("Назва клітини:"))
        layout.addWidget(self.name_input)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Опишіть клітину...")
        layout.addWidget(QLabel("Опис клітини (текст):"))
        layout.addWidget(self.description_input)

        self.generate_button = QPushButton("Згенерувати JSON")
        self.generate_button.clicked.connect(self.generate_json)
        layout.addWidget(self.generate_button)

        self.json_output = QTextEdit()
        layout.addWidget(QLabel("JSON результат:"))
        layout.addWidget(self.json_output)

        self.save_button = QPushButton("Зберегти клітину")
        self.save_button.clicked.connect(self.save_cell)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def generate_json(self):
        description = self.description_input.toPlainText().strip()
        name = self.name_input.text().strip()
        openai.api_key = self.api_key

        prompt = (
            f"Назва клітини: {name}\n"
            f"Опис: {description}\n\n"
            "Згенеруй JSON-структуру клітини для симуляції. "
            "Формат має бути такий:\n"
            "{\n"
            '  "type": "immune" або "tumor",\n'
            f'  "name": "{name}",\n'
            '  "color": [R, G, B],\n'
            '  "rates": {\n'
            '    "apoptosis": float,\n'
            '    "proliferation": float,\n'
            '    "migration": float\n'
            '  }\n'
            "}\n"
            "Поверни лише валідний JSON без пояснень чи коментарів."
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ти генератор клітин для симулятора."},
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content.strip()
            self.json_output.setPlainText(result)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def save_cell(self):
        try:
            json_data = json.loads(self.json_output.toPlainText())
            file_path, _ = QFileDialog.getSaveFileName(self, "Зберегти JSON", "", "JSON Files (*.json)")
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Успіх", "Клітина збережена!")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Помилка", "Невірний JSON формат.")
