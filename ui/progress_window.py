from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PySide2.QtCore import Qt, QTimer


class ProgressWindow(QWidget):
    def __init__(self, message="Processing...", duration=2000, on_complete=None):
        super().__init__()
        self.setWindowTitle("Please Wait")
        self.setFixedSize(300, 100)
        # self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        self.setWindowModality(Qt.ApplicationModal)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.on_complete = on_complete

        # Start the timer
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.complete)
        self.timer.start(duration)

    def complete(self):
        if self.on_complete:
            self.on_complete()
        self.close()
