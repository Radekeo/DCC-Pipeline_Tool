from PySide2.QtWidgets import QApplication
from ui.start_window import StartWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec_())

__main__()