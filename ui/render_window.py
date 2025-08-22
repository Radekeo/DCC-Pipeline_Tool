import os
from PySide2.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QCheckBox
)
from PySide2.QtCore import Qt

from ui.progress_window import ProgressWindow
from core.rendering import RenderSettings, Renderer, RenderManager
from core.utils import list_cameras_in_usd


class RenderSettingsWindow(QWidget):
    def __init__(self, dir, project=None, shot=None):
        super().__init__()
        self.project = project
        self.shot = shot
        self.project_dir = dir
        self.output_path = os.path.join(self.project_dir, "Renders")

        # Render manager
        self.renders_yaml = os.path.join(self.project_dir, "Config", "renders.yaml")
        self.rm = RenderManager(self.renders_yaml)

        self.setWindowTitle("Render Settings")
        self.setFixedSize(450, 420)

        # --- Renderer Dropdown ---
        self.renderer_label = QLabel("Renderer:")
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["Arnold", "Karma", "Renderman"])
        self.renderer_combo.currentIndexChanged.connect(self.update_formats)

        renderer_layout = QHBoxLayout()
        renderer_layout.addWidget(self.renderer_label)
        renderer_layout.addWidget(self.renderer_combo)

        # --- Output Format Dropdown ---
        self.format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        format_layout = QHBoxLayout()
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_combo)

        # --- Resolution Settings ---
        self.res_label = QLabel("Resolution:")
        self.res_width = QSpinBox(); self.res_width.setRange(16, 8192); self.res_width.setValue(1920)
        self.res_height = QSpinBox(); self.res_height.setRange(16, 8192); self.res_height.setValue(1080)

        res_layout = QHBoxLayout()
        res_layout.addWidget(self.res_label)
        res_layout.addWidget(QLabel("W")); res_layout.addWidget(self.res_width)
        res_layout.addWidget(QLabel("H")); res_layout.addWidget(self.res_height)

        # --- FPS ---
        self.fps_label = QLabel("FPS:")
        self.fps_input = QSpinBox(); self.fps_input.setRange(1, 240); self.fps_input.setValue(24)

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(self.fps_label)
        fps_layout.addWidget(self.fps_input)

        # --- Frame Range ---
        self.frame_label = QLabel("Frame Range:")
        self.start_frame = QSpinBox(); self.start_frame.setRange(0, 10000); self.start_frame.setValue(1)
        self.end_frame = QSpinBox(); self.end_frame.setRange(0, 10000); self.end_frame.setValue(100)

        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.frame_label)
        frame_layout.addWidget(QLabel("Start")); frame_layout.addWidget(self.start_frame)
        frame_layout.addWidget(QLabel("End")); frame_layout.addWidget(self.end_frame)

        # --- Options ---
        self.motion_blur = QCheckBox("Motion Blur")
        self.denoise = QCheckBox("Denoise")
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.motion_blur)
        options_layout.addWidget(self.denoise)

        # --- Karma-specific (hidden by default) ---
        self.camera_label = QLabel("Camera:")
        self.camera_combo = QComboBox()
        self.camera_label.hide(); self.camera_combo.hide()

        self.light_label = QLabel("Light:")
        self.light_combo = QComboBox(); self.light_combo.addItems(["None", "Dome Light", "Physical Sky"])
        self.light_label.hide(); self.light_combo.hide()

        # --- Render Button ---
        self.render_button = QPushButton("Render")
        self.render_button.clicked.connect(self.start_render)

        # --- Error Label ---
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red")

        # --- Main Layout ---
        layout = QVBoxLayout()
        layout.addLayout(renderer_layout)
        layout.addLayout(format_layout)
        layout.addLayout(res_layout)
        layout.addLayout(fps_layout)
        layout.addLayout(frame_layout)
        layout.addLayout(options_layout)
        layout.addWidget(self.camera_label); layout.addWidget(self.camera_combo)
        layout.addWidget(self.light_label); layout.addWidget(self.light_combo)
        layout.addWidget(self.error_label)
        layout.addStretch()
        layout.addWidget(self.render_button)
        self.setLayout(layout)

        self.update_formats()

    # -------------------------
    def update_formats(self):
        renderer = self.renderer_combo.currentText()

        if renderer == "Arnold":
            self.format_combo.clear(); self.format_combo.addItems(["EXR", "PNG"])
        elif renderer == "Renderman":
            self.format_combo.clear(); self.format_combo.addItems(["EXR"])
        elif renderer == "Karma":
            self.format_combo.clear(); self.format_combo.addItems(["EXR", "PNG", "JPEG"])

            # Show camera/light options
            self.camera_label.show(); self.camera_combo.show()
            self.light_label.show(); self.light_combo.show()

            # Populate cameras
            if self.project and "scene_file" in self.project:
                scene_files = self.project.get("scene_file", [])
                if not isinstance(scene_files, list):
                    raise ValueError("Expected scene_file to be a list of files")

                # Find the first USD file (.usd/.usda/.usdc)
                usd_file = next(
                    (f for f in scene_files if f.lower().endswith((".usd", ".usda", ".usdc"))),
                    None
                )
                if not usd_file:
                    raise ValueError("No USD scene file found in project['scene_file']")

                usd_scene_path = os.path.join(self.project_dir, "Scene", usd_file)

                # scene_path = os.path.join(self.project_dir, self.project.get('scene_file'))
                print(f"!!!!!THIS WORKED AND SCENE FILE IS {self.project.get('scene_file')}!!!!!!")
                cameras = list_cameras_in_usd(usd_scene_path)
                self.camera_combo.clear()
                self.camera_combo.addItems(cameras or ["<No Cameras Found>"])
        else:
            self.camera_label.hide(); self.camera_combo.hide()
            self.light_label.hide(); self.light_combo.hide()

    # -------------------------
    def validate_inputs(self):
        if self.start_frame.value() > self.end_frame.value():
            self.error_label.setText("Start frame cannot be greater than end frame.")
            return False
        self.error_label.setText("")
        return True

    # -------------------------
    def start_render(self):
        if not self.validate_inputs():
            return

        settings = RenderSettings(
            renderer=self.renderer_combo.currentText(),
            fps=self.fps_input.value(),
            output_dir=self.output_path,
            output_format=self.format_combo.currentText(),
            resolution_width=self.res_width.value(),
            resolution_height=self.res_height.value(),
            motion_blur=self.motion_blur.isChecked(),
            denoise=self.denoise.isChecked()
        )

        # if settings.renderer == "Karma":
        settings.camera = self.camera_combo.currentText()
        settings.light = self.light_combo.currentText()

        # Create new render version
        rsv = self.rm.new_render_version(settings)
        renderer = Renderer(settings, metadata=self.project, rsv=rsv)

        # For now: single batch job
        self.progress = ProgressWindow(
            message=f"Rendering ...",
            determinate=True,
            maximum=(self.end_frame.value() - self.start_frame.value() + 1)
        )
        self.progress.show()

        def progress_callback(idx, total, frame):
            pct = idx / total * 100
            self.progress.update_message(f"Rendering... {pct:.0f}%")
            self.progress.update_progress(idx)
            QApplication.processEvents()
            self.rm.update_frame(rsv, frame)
            if idx == total:
                self.progress.task_done()

        total = self.end_frame.value() - self.start_frame.value() + 1
        for idx, frame in enumerate(range(self.start_frame.value(), self.end_frame.value() + 1), start=1):
            renderer.render_shot({"frame": frame})
            progress_callback(idx, total, frame)
