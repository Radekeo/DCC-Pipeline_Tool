from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PySide2.QtCore import Qt, QTimer, QThreadPool

class ProgressWindow(QWidget):
    def __init__(self, message="Processing...", duration=None, worker=None, on_complete=None, determinate=False, maximum=100):
        super().__init__()
        self.setWindowTitle("Please Wait")
        self.setFixedSize(300, 100)
        self.setWindowModality(Qt.ApplicationModal)
        self.setStyleSheet("background-color: white;")

        # --- Label ---
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)

        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        if determinate:
            self.progress_bar.setRange(0, maximum)  # determinate
        else:
            self.progress_bar.setRange(0, 0)  # indeterminate (spinning)

        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        self.on_complete = on_complete
        self.worker = worker
        self.duration = duration

        # Worker support
        if self.worker:
            QThreadPool.globalInstance().start(self.worker)
            self.worker.signals.finished.connect(self.task_done)
        elif self.duration:
            QTimer.singleShot(self.duration, self.task_done)


    # def render_with_progress(adapter, progress_callback):
    #     for idx, frame in enumerate(range(adapter.start_frame, adapter.end_frame + 1), 1):
    #         adapter.render_frame(frame)  # single frame render method
    #         progress_callback(idx, adapter.end_frame - adapter.start_frame + 1)


    # --- Public API ---
    def update_message(self, new_message: str):
        self.label.setText(new_message)

    def update_progress(self, value: int):
        """Update progress bar if determinate."""
        if self.progress_bar.maximum() > 0:
            self.progress_bar.setValue(value)

    def task_done(self):
        self.close()
        if callable(self.on_complete):
            self.on_complete()
