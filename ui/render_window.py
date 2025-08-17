import os

from PySide2.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QLineEdit, QFileDialog, QCheckBox
)
from PySide2.QtCore import Qt
from ui.progress_window import ProgressWindow


class RenderSettingsWindow(QWidget):
    def __init__(self, dir, project=None, shot=None):
        """
        :param project: Reference to current project metadata (from Window 2)
        :param shot: Optional current shot
        """
        super().__init__()
        self.project = project
        self.shot = shot
        self.project_dir = dir
        self.output_path = os.path.join(self.project_dir, "Renders")

        self.setWindowTitle("Render Settings")
        self.setFixedSize(450, 350)

        # --- Renderer Dropdown ---
        self.renderer_label = QLabel("Renderer:")
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["Arnold", "Redshift", "Karma", "Other"])
        self.renderer_combo.currentIndexChanged.connect(self.update_formats)

        renderer_layout = QHBoxLayout()
        renderer_layout.addWidget(self.renderer_label)
        renderer_layout.addWidget(self.renderer_combo)

        # --- Output Format Dropdown ---
        self.format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["EXR", "PNG", "JPEG"])
        self.format_layout = QHBoxLayout()
        self.format_layout.addWidget(self.format_label)
        self.format_layout.addWidget(self.format_combo)

        # --- Resolution Settings ---
        self.res_label = QLabel("Resolution:")
        self.res_width = QSpinBox()
        self.res_width.setRange(16, 8192)
        self.res_width.setValue(1920)
        self.res_height = QSpinBox()
        self.res_height.setRange(16, 8192)
        self.res_height.setValue(1080)

        res_layout = QHBoxLayout()
        res_layout.addWidget(self.res_label)
        res_layout.addWidget(QLabel("W"))
        res_layout.addWidget(self.res_width)
        res_layout.addWidget(QLabel("H"))
        res_layout.addWidget(self.res_height)

        # --- FPS Setting ---
        self.fps_label = QLabel("FPS:")
        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 240)
        self.fps_input.setValue(24)

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(self.fps_label)
        fps_layout.addWidget(self.fps_input)

        # --- Frame Range ---
        self.frame_label = QLabel("Frame Range:")
        self.start_frame = QSpinBox()
        self.start_frame.setRange(0, 10000)
        self.start_frame.setValue(1)
        self.end_frame = QSpinBox()
        self.end_frame.setRange(0, 10000)
        self.end_frame.setValue(240)

        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.frame_label)
        frame_layout.addWidget(QLabel("Start"))
        frame_layout.addWidget(self.start_frame)
        frame_layout.addWidget(QLabel("End"))
        frame_layout.addWidget(self.end_frame)


        # --- Optional Checkboxes ---
        self.motion_blur = QCheckBox("Motion Blur")
        self.denoise = QCheckBox("Denoise")

        options_layout = QHBoxLayout()
        options_layout.addWidget(self.motion_blur)
        options_layout.addWidget(self.denoise)

        # --- Render Button ---
        self.render_button = QPushButton("Render")
        self.render_button.clicked.connect(self.start_render)

        # --- Error / Info Label ---
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red")

        # --- Main Layout ---
        layout = QVBoxLayout()
        layout.addLayout(renderer_layout)
        layout.addLayout(self.format_layout)
        layout.addLayout(res_layout)
        layout.addLayout(fps_layout)
        layout.addLayout(frame_layout)
        # layout.addLayout(path_layout)
        layout.addLayout(options_layout)
        layout.addWidget(self.error_label)
        layout.addStretch()
        layout.addWidget(self.render_button)
        self.setLayout(layout)

        # Initialize dynamic updates
        self.update_formats()

    # --- Methods ---
    def update_formats(self):
        """Update available formats depending on selected renderer."""
        renderer = self.renderer_combo.currentText()
        if renderer == "Arnold":
            self.format_combo.clear()
            self.format_combo.addItems(["EXR", "PNG"])
        elif renderer == "Redshift":
            self.format_combo.clear()
            self.format_combo.addItems(["EXR", "JPEG"])
        else:
            self.format_combo.clear()
            self.format_combo.addItems(["PNG", "JPEG"])

    def browse_output(self):
        """Open a dialog to select output directory."""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.path_input.setText(path)

    def validate_inputs(self):
        """Check all inputs are valid before starting render."""
        
        if self.start_frame.value() > self.end_frame.value():
            self.error_label.setText("Start frame cannot be greater than end frame.")
            return False
        self.error_label.setText("")
        return True

    def start_render(self):
        if not self.validate_inputs():
            return

        # Collect render settings
        settings = {
            "renderer": self.renderer_combo.currentText(),
            "format": self.format_combo.currentText(),
            "resolution": [self.res_width.value(), self.res_height.value()],
            "fps": self.fps_input.value(),
            "frame_range": [self.start_frame.value(), self.end_frame.value()],
            "output_path": self.output_path,
            "motion_blur": self.motion_blur.isChecked(),
            "denoise": self.denoise.isChecked(),
        }

        print("Render started with settings:", settings)

        # Show progress window and close self
        self.progress = ProgressWindow(
            message="Rendering...",
            duration=4000,
            on_complete=self.close
        )
        self.progress.show()
