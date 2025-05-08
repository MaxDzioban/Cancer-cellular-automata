import sys
from PyQt5.QtWidgets import QApplication
from visualization import MainMenu


app = QApplication(sys.argv)
api_key = "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"
main_menu = MainMenu(api_key)
main_menu.show()
sys.exit(app.exec_())