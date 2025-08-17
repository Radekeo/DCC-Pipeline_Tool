import os
import logging
import yaml

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,  QLineEdit, QListWidget,QListWidgetItem,
    QSplitter, QTreeWidget, QTreeWidgetItem, QMessageBox
)
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QIcon, QImage, QPainter
# from pxr import Usd, UsdImagingGL, Gf

from ui.progress_window import ProgressWindow
from ui.render_window import RenderSettingsWindow


class MainProjectWindow(QWidget):
    def __init__(self, metadata_file=None, metadata=None):
        super().__init__()
        self.metadata_file = metadata_file
        
        if self.metadata_file:
            self.metadata = self.load_metadata(self.metadata_file)
        elif metadata:
            self.metadata = metadata
        else:
            raise ValueError("Must provide either metadata or metadata_file")

        self.scene_file = self.metadata.get("scene_file", "No scene file")
        self.project_path = self.metadata.get("project_dir", "")
        
        self.logger = logging.getLogger(__name__)

        self.setWindowTitle(f"Project - {self.metadata.get('project_name', 'Untitled')}")
        self.setMinimumSize(800, 500)

        # --- Left: Viewport ---
        # Load Stage
        # usd_path = os.path.join(self.project_path, self.scene_file)
        # self.viewport = USDViewportWidget(usd_path)

        # Create and embed usdviewq widget
        # self.viewport = Usdviewq.ViewerWidget()
        # self.viewport.setStage(stage)
        self.viewport = QLabel(f"USD Viewport Placeholder\n({self.scene_file})")
        self.viewport.setAlignment(Qt.AlignCenter)
        self.viewport.setStyleSheet("border: 1px solid gray;")

        # --- Right: Project structure + controls ---
        self.project_structure = QTreeWidget()
        self.project_structure.setHeaderHidden(True)

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

        self.refresh_project_structure()

    def load_metadata(self, file_path):
        try:
            with open(file_path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}


    def get_project_structure_dict(self):
        """
        Helper: return the current QTreeWidget structure as a nested dict.
        Makes testing much easier.
        """
        def item_to_dict(item):
            return {
                "name": item.text(0),
                "children": [item_to_dict(item.child(i)) for i in range(item.childCount())]
            }

        structure = []
        for i in range(self.project_structure.topLevelItemCount()):
            structure.append(item_to_dict(self.project_structure.topLevelItem(i)))
        return structure

        
    def refresh_project_structure(self):
        """Scan project 'Shots' directory and list shots + renders."""
        self.project_structure.clear()
        shot_list = self.metadata.get('shots', [])
        shot_struct = self.metadata.get("shot_struct", {})
        renders = self.metadata.get("renders", {})
        render_settings = self.metadata.get("renderSettings", {})
        
        # Folder icon for Shots root
        shots_item = QTreeWidgetItem(["Shots"])
        shots_item.setIcon(0, QIcon.fromTheme("folder"))
        self.project_structure.addTopLevelItem(shots_item)
        
        if shot_list:
            for shot_name in shot_list:
                shot_item = QTreeWidgetItem([shot_name])
                shot_item.setIcon(0, QIcon.fromTheme("image-x-generic"))
                shots_item.addChild(shot_item)

                # Frames
                frames = shot_struct.get(shot_name)
                if frames and isinstance(frames, (tuple, list)) and len(frames) == 2:
                    for i in range(frames[0], frames[1] + 1):  # ✅ inclusive range
                        frame_item = QTreeWidgetItem([f"Frame {i}"])
                        frame_item.setIcon(0, QIcon.fromTheme("text-x-generic"))
                        shot_item.addChild(frame_item)
                else:
                    self.logger.warning(f"Invalid frame data for shot '{shot_name}': {frames}")                   
        else:
            no_shots_item = QTreeWidgetItem(["No shots found"])
            shots_item.addChild(no_shots_item)

    def open_manage_shots(self):
        # print("Opening Manage Shots window (Window 3)…")
        self.shots_manager = ManageShotsWindow(main_window=self)
        self.shots_manager.show()
        # Placeholder for now

    def test_render(self):
        print("Simulating test render…")
        self.progress = ProgressWindow(
            message="Test rendering frame...",
            duration=2000
        )
        self.progress.show()

    def open_render_settings(self):
        self.render_settings = RenderSettingsWindow()
        self.render_settings.show()
        # print("Opening Render Settings window (Window 4)…")
        # Placeholder for now

    def closeEvent(self, event):
        print("Closing Project Window. Exiting application.")
        event.accept()


class ManageShotsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Manage Shots")
        self.setFixedSize(500, 400)
        self.main_window = main_window  # reference to MainProjectWindow

        # Simulated frame range (placeholder if needed)
        self.frame_count = 100  
        self.frame_label = QLabel(f"Total Frames: {self.frame_count}")

        # Shot input: name and frame range
        self.shot_name_input = QLineEdit()
        self.shot_name_input.setPlaceholderText("Shot name (e.g. ShotA)")

        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("Frame range (e.g. 1-24)")

        self.add_button = QPushButton("Add Shot")
        self.add_button.clicked.connect(self.add_shot)

        self.update_button = QPushButton("Update Selected")
        self.update_button.clicked.connect(self.update_shot)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_shot)

        # Shots list
        self.shot_list = QListWidget()
        self.refresh_shot_list()

        # Done / Cancel buttons
        done_button = QPushButton("Done")
        cancel_button = QPushButton("Cancel")
        done_button.clicked.connect(self.done)
        cancel_button.clicked.connect(self.cancel)

        # Layouts
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.shot_name_input)
        input_layout.addWidget(self.range_input)
        input_layout.addWidget(self.add_button)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.update_button)
        action_layout.addWidget(self.delete_button)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(done_button)

        layout = QVBoxLayout()
        layout.addWidget(self.frame_label)
        layout.addLayout(input_layout)
        layout.addLayout(action_layout)
        layout.addWidget(self.shot_list)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def refresh_shot_list(self):
        """Load shots from main_window metadata into the list widget."""
        self.shot_list.clear()
        shots = self.main_window.metadata.get("shots", [])
        shot_struct = self.main_window.metadata.get("shot_struct", {})

        for shot_name in shots:
            frames = shot_struct.get(shot_name, [])
            item_text = f"{shot_name} ({frames[0]}-{frames[1]})" if frames else shot_name
            self.shot_list.addItem(QListWidgetItem(item_text))

    def add_shot(self):
        name = self.shot_name_input.text().strip()
        range_text = self.range_input.text().strip()

        if not name or not range_text:
            QMessageBox.warning(self, "Input Error", "Please provide both shot name and frame range.")
            return

        try:
            start, end = [int(x) for x in range_text.split("-")]
        except Exception:
            QMessageBox.warning(self, "Input Error", "Frame range must be in format start-end (e.g. 1-24).")
            return

        # Update main_window metadata
        shots = self.main_window.metadata.setdefault("shots", [])
        shot_struct = self.main_window.metadata.setdefault("shot_struct", {})

        if name in shots:
            QMessageBox.warning(self, "Duplicate Shot", f"Shot '{name}' already exists.")
            return

        shots.append(name)
        shot_struct[name] = [start, end]

        # Update UI
        self.shot_name_input.clear()
        self.range_input.clear()
        self.refresh_shot_list()
        self.main_window.refresh_project_structure()
        self.save_metadata()

    def update_shot(self):
        selected_item = self.shot_list.currentItem()
        if not selected_item:
            return

        old_text = selected_item.text()
        old_name = old_text.split()[0]

        new_name = self.shot_name_input.text().strip() or old_name
        range_text = self.range_input.text().strip()
        shot_struct = self.main_window.metadata.get("shot_struct", {})

        if range_text:
            try:
                start, end = [int(x) for x in range_text.split("-")]
            except Exception:
                QMessageBox.warning(self, "Input Error", "Frame range must be in format start-end (e.g. 1-24).")
                return
            shot_struct[new_name] = [start, end]

        # Rename if necessary
        shots = self.main_window.metadata.get("shots", [])
        
        if new_name != old_name:
            if new_name in shots:
                QMessageBox.warning(self, "Duplicate Shot", f"Shot '{new_name}' already exists.")
                return
            shots[shots.index(old_name)] = new_name
            if old_name in shot_struct and new_name not in shot_struct:
                shot_struct[new_name] = shot_struct.pop(old_name)
            elif old_name in shot_struct:
                shot_struct.pop(old_name)


        # if new_name != old_name:
        #     if new_name in shots:
        #         QMessageBox.warning(self, "Duplicate Shot", f"Shot '{new_name}' already exists.")
        #         return
        #     shots[shots.index(old_name)] = new_name
        #     if old_name in shot_struct:
        #         shot_struct[new_name] = shot_struct.pop(old_name)

        self.shot_name_input.clear()
        self.range_input.clear()
        self.refresh_shot_list()
        self.main_window.refresh_project_structure()
        self.save_metadata()

    def delete_shot(self):
        selected_item = self.shot_list.currentItem()
        if not selected_item:
            return

        name = selected_item.text().split()[0]
        shots = self.main_window.metadata.get("shots", [])
        shot_struct = self.main_window.metadata.get("shot_struct", {})

        if name in shots:
            shots.remove(name)
        if name in shot_struct:
            shot_struct.pop(name)

        self.refresh_shot_list()
        self.main_window.refresh_project_structure()
        self.save_metadata()

    def save_metadata(self):
        """Write current metadata to YAML file."""
        if hasattr(self.main_window, "metadata_file"):
            with open(self.main_window.metadata_file, "w") as f:
                yaml.safe_dump(self.main_window.metadata, f)

    def done(self):
        self.close()

    def cancel(self):
        self.close()

# class USDViewportWidget(QWidget):
#     def __init__(self, usd_file, parent=None):
#         super().__init__(parent)
#         self.usd_file = usd_file
#         self.stage = Usd.Stage.Open(self.usd_file)

#         # Imaging engine
#         self.renderer = UsdImagingGL.Engine()
#         self.camera_path = "/__Cam__"

#         # Set a default camera if none in the scene
#         self._setup_default_camera()

#         # Refresh every 100ms (can be reduced for performance)
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update)
#         self.timer.start(100)

#     def _setup_default_camera(self):
#         # Use a synthetic camera if not found in USD file
#         self.renderer.SetCameraState(
#             Gf.Matrix4d(1.0),  # Identity view matrix
#             Gf.Range1d(0.1, 1000.0)  # Near / far clipping planes
#         )

#     def paintEvent(self, event):
#         painter = QPainter(self)

#         # Create a framebuffer (RGBA8)
#         width, height = self.width(), self.height()
#         framebuffer = UsdImagingGL.Framebuffer(width, height)

#         # Render scene
#         self.renderer.Render(self.stage.GetPseudoRoot(), framebuffer)

#         # Convert to QImage
#         image_data = framebuffer.colorBuffer
#         qimage = QImage(image_data, width, height, QImage.Format_RGBA8888)

#         # Draw to widget
#         painter.drawImage(0, 0, qimage)
#         painter.end()