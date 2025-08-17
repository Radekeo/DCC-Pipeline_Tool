from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QDialog, QProgressBar
from PySide2.QtCore import Qt, QTimer, QThread, QThreadPool

class ProgressWindow(QWidget):
    def __init__(self, message="Processing...", duration=None, worker=None, on_complete=None):
        super().__init__()
        self.setWindowTitle("Please Wait")
        self.setFixedSize(300, 100)
        # self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        self.setWindowModality(Qt.ApplicationModal)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) 

        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        self.on_complete = on_complete
        self.worker = worker
        self.duration = duration

        if self.worker:
            # Run worker in QThreadPool
            QThreadPool.globalInstance().start(self.worker)
            self.worker.signals.finished.connect(self.task_done)
        elif self.duration:
            QTimer.singleShot(self.duration, self.task_done)
            # self.on_complete = on_complete

        # Start the timer
        # if duration > 0:
        #     QTimer.singleShot(duration, self.complete)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.complete)
        self.timer.start(duration)

    def task_done(self):
        self.close()
        if callable(self.on_complete):
            self.on_complete()

    def complete(self):
        if self.on_complete:
            self.close()
        