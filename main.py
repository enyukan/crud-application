from PySide6.QtWidgets import QApplication
from pages.login import LoginPage
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginPage()
    window.show()
    sys.exit(app.exec())
