from PySide2.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox
)
from PySide2.QtCore import Qt
from ui.progress_window import ProgressWindow


class RenderSettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Render Settings")
        self.setFixedSize(400, 200)

        # --- Renderer Dropdown ---
        renderer_label = QLabel("Renderer:")
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["Arnold", "Redshift", "Karma", "Other"])

        renderer_layout = QHBoxLayout()
        renderer_layout.addWidget(renderer_label)
        renderer_layout.addWidget(self.renderer_combo)

        # --- FPS Setting ---
        fps_label = QLabel("FPS:")
        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 240)
        self.fps_input.setValue(24)

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(fps_label)
        fps_layout.addWidget(self.fps_input)

        # --- Render Button ---
        render_button = QPushButton("Render")
        render_button.clicked.connect(self.start_render)

        # --- Main Layout ---
        layout = QVBoxLayout()
        layout.addLayout(renderer_layout)
        layout.addLayout(fps_layout)
        layout.addStretch()
        layout.addWidget(render_button)
        self.setLayout(layout)

    def start_render(self):
        # Simulate starting the render (shell stage)
        selected_renderer = self.renderer_combo.currentText()
        fps_value = self.fps_input.value()
        print(f"Render started with: {selected_renderer}, FPS: {fps_value}")

        # Show progress window and close self
        self.progress = ProgressWindow(
            message="Rendering...",
            duration=4000,
            on_complete=self.close
        )
        self.progress.show()
