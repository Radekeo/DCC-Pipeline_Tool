from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.job import submit_job


class RenderConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Render Job Settings")
        layout = QVBoxLayout()

        self.scene_input = QLineEdit()
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["Arnold", "Mantra"])
        self.frame_range = QLineEdit("1-100")
        self.resolution = QLineEdit("1920x1080")

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.handle_submit)

        layout.addWidget(QLabel("Scene File Path"))
        layout.addWidget(self.scene_input)
        layout.addWidget(QLabel("Renderer"))
        layout.addWidget(self.renderer_combo)
        layout.addWidget(QLabel("Frame Range"))
        layout.addWidget(self.frame_range)
        layout.addWidget(QLabel("Resolution"))
        layout.addWidget(self.resolution)
        layout.addWidget(submit_btn)

        self.setLayout(layout)

    def handle_submit(self):
        scene = self.scene_input.text()
        renderer = self.renderer_combo.currentText()
        frames = self.frame_range.text()
        resolution = self.resolution.text()

        # Pass to backend logic
        submit_render_job(scene, renderer, frames, resolution)
        self.accept()