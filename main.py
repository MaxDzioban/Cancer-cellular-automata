import sys
from PyQt5.QtWidgets import QApplication
from visualization import MainMenu


app = QApplication(sys.argv)
api_key = "OPEN_AI_api_key"
main_menu = MainMenu(api_key)
main_menu.show()
sys.exit(app.exec_())
