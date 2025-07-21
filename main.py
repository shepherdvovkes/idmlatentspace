import sys
from PySide6.QtWidgets import QApplication
from gui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Установка стиля для современного вида
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
