from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,  QLineEdit, QListWidget,QListWidgetItem,
    QSplitter
)

from PySide2.QtCore import Qt
from render_window import RenderSettingsWindow


class ProjectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Window")
        self.setMinimumSize(800, 500)

        # --- Left: Viewport placeholder ---
        self.viewport = QLabel("USD Viewport Placeholder")
        self.viewport.setAlignment(Qt.AlignCenter)
        self.viewport.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")

        # --- Right: Project structure + controls ---
        self.project_structure = QListWidget()
        self.project_structure.addItems(["Shot 01", "Shot 02", "Rendered Assets", "…"])

        self.manage_shots_btn = QPushButton("Manage Shots")
        self.test_render_btn = QPushButton("Test Render")
        self.render_settings_btn = QPushButton("Render Settings")

        self.manage_shots_btn.clicked.connect(self.open_manage_shots)
        self.test_render_btn.clicked.connect(self.test_render)
        self.render_settings_btn.clicked.connect(self.open_render_settings)

        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Project Structure"))
        right_panel.addWidget(self.project_structure)
        right_panel.addWidget(self.manage_shots_btn)
        right_panel.addWidget(self.test_render_btn)
        right_panel.addWidget(self.render_settings_btn)
        right_panel.addStretch()

        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        # --- Split view ---
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.viewport)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 200])  # adjust initial proportions

        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def open_manage_shots(self):
        self.shot_window = ManageShotsWindow()
        self.shot_window.show()
        # Placeholder for now

    def test_render(self):
        print("Simulating test render…")
        from progress_window import ProgressWindow
        self.progress = ProgressWindow(
            message="Test rendering frame...",
            duration=2000
        )
        self.progress.show()

    def open_render_settings(self):
        self.render_settings_window = RenderSettingsWindow()
        self.render_settings_window.show()


    def closeEvent(self, event):
        print("Closing Project Window. Exiting application.")
        event.accept()


class ManageShotsWindow(QWidget):
    def __init__(self, on_done=None, on_cancel=None):
        super().__init__()
        self.setWindowTitle("Manage Shots")
        self.setFixedSize(500, 400)
        self.on_done = on_done
        self.on_cancel = on_cancel

        # Simulated frame range
        self.frame_count = 100  # Placeholder for actual frame count
        self.frame_label = QLabel(f"Total Frames: {self.frame_count}")

        # Shot input
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g. 1-24")

        self.add_button = QPushButton("Add Shot")
        self.add_button.clicked.connect(self.add_shot)

        # Shots list
        self.shot_list = QListWidget()

        # Buttons
        done_button = QPushButton("Done")
        cancel_button = QPushButton("Cancel")
        done_button.clicked.connect(self.done)
        cancel_button.clicked.connect(self.cancel)

        # Layouts
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.range_input)
        input_layout.addWidget(self.add_button)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(done_button)

        layout = QVBoxLayout()
        layout.addWidget(self.frame_label)
        layout.addLayout(input_layout)
        layout.addWidget(self.shot_list)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def add_shot(self):
        range_text = self.range_input.text().strip()
        if range_text:
            self.shot_list.addItem(QListWidgetItem(f"Shot: {range_text}"))
            self.range_input.clear()

    def done(self):
        # You can later collect shot ranges here
        if self.on_done:
            self.on_done()
        self.close()

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.close()

    def closeEvent(self, event):
        if self.on_cancel:
            self.on_cancel()
        event.accept()