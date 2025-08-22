import sys
import time
import os
from PySide2.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QFileDialog
)
from PySide2.QtCore import Qt

from ui.progress_window import ProgressWindow
from ui.project_window import MainProjectWindow
from core.utils import check_file_type 
from core.project import SceneProject


class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DCC Pipeline Tool - Start")
        self.setFixedSize(300, 150)

        # Buttons
        self.create_button = QPushButton("Create New Project")
        self.open_button = QPushButton("Open Existing Project")

        # Connect signals
        self.create_button.clicked.connect(self.open_create_project_window)
        self.open_button.clicked.connect(self.open_existing_project_window)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.create_button)
        layout.addWidget(self.open_button)
        self.setLayout(layout)

        # References to modal windows
        self.create_window = None
        self.open_window = None

    def open_create_project_window(self):
        self.setEnabled(False)
        self.create_window = NewProjectWindow(
            on_cancel=self.on_child_cancel,
            on_success=self.close_start
        )
        self.create_window.show()

    def open_existing_project_window(self):
        self.setEnabled(False)
        self.open_window = ExistingProjectWindow(
            on_cancel=self.on_child_cancel,
            on_success=self.close_start
        )
        self.open_window.show()

    def on_child_cancel(self):
        self.setEnabled(True)

    def close_start(self):
        self.close()


class NewProjectWindow(QWidget):
    def __init__(self, on_cancel, on_success):
        super().__init__()
        self.setWindowTitle("DCC Pipeline Tool - New Project")
        self.setFixedSize(400, 220)
        self.on_cancel = on_cancel
        self.on_success = on_success

        # --- Error label ---
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.hide()

        # --- Project name field ---
        name_label = QLabel("Project Name:")
        self.name_input = QLineEdit()
        self.name = self.name_input.text().strip()

        name_layout = QHBoxLayout()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)

        # --- File selection field ---
        file_label = QLabel("Project File:")
        self.file_display = QLineEdit()
        self.file_display.setReadOnly(True)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.select_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_display)
        file_layout.addWidget(browse_button)

        # --- Buttons ---
        create_button = QPushButton("Create Project")
        cancel_button = QPushButton("Cancel")

        create_button.clicked.connect(self.create_project)
        cancel_button.clicked.connect(self.cancel)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(create_button)

        # --- Main Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.error_label)  # add error display
        layout.addLayout(name_layout)
        layout.addLayout(file_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Project File", "", "Scene Files (*.usda *.usdc *.usd *.ma *.mb *.hip *.hipnc)"
        )

        if not file_path:
            return

        # file_type = check_file_type(file_path)
        # if not file_type:
        #     self.error_label.setText("Unsupported file type selected.")
        #     self.error_label.show()
        #     return

        self.error_label.hide()
        self.file_display.setText(file_path)  # Just show selected file path


    def create_project(self):
        project_name = self.name_input.text().strip()
        file_path = self.file_display.text().strip()

        if not project_name or not file_path:
            self.error_label.setText("Project name and file are required.")
            self.error_label.show()
            return

        self.error_label.hide()

        file_type = check_file_type(file_path)

        def after_progress():
            try:
                np = SceneProject()
                np.create_new(project_name, file_path, file_type)

                # Open main project window
                self.metadata_file, self.metadata = np.config.load()
                self.project_window = MainProjectWindow(metadata_file=self.metadata_file)
                self.project_window.show()
                self.on_success()
                self.close()

            except FileExistsError as e:
                self.error_label.setText(str(e))
                self.error_label.show()
            except Exception as e:
                self.error_label.setText(f"Error creating project: {e}")
                self.error_label.show()

        # Simulate longer progress window for non-USD files
        progress_duration = 5000 if file_type in ["maya", "houdini"] else 2000

        self.progress = ProgressWindow(
            message="Creating project...",
            duration=progress_duration,
            on_complete=after_progress
        )


        self.progress.show()
        self.close()

    def cancel(self):
        self.close()
        self.on_cancel()

    def closeEvent(self, event):
        self.on_cancel()
        event.accept()

class ExistingProjectWindow(QWidget):
    def __init__(self, on_cancel, on_success):
        super().__init__()
        self.setWindowTitle("DCC Pipeline Tool - Open Project")
        self.setFixedSize(400, 150)
        self.on_cancel = on_cancel
        self.on_success = on_success

        # --- Project tag input with button beside ---
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter project tag (e.g., @MyProject)")

        load_button = QPushButton("Load Project")
        load_button.clicked.connect(self.load_project)

        tag_row = QHBoxLayout()
        tag_row.addWidget(self.tag_input)
        tag_row.addWidget(load_button)

        # --- Error label ---
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.hide()

        # --- Main layout ---
        layout = QVBoxLayout()
        layout.addLayout(tag_row)
        layout.addWidget(self.error_label)
        self.setLayout(layout)

        # Scene Project
        self.sp = SceneProject()

    def load_project(self):
        project_tag = self.tag_input.text().strip()

        if not project_tag:
            self.setWindowTitle("Enter a project tag!")
            return

        def after_progress():
            try:
                self.metadata = self.sp.load_existing(project_tag)
                self.project_dir = self.metadata.get("project_dir", "")
                project_config_path = os.path.join(self.project_dir, "Config", "metadata.yaml")

                # Open Project
                self.project_window = MainProjectWindow(metadata_file=project_config_path)
                self.project_window.show()

                self.on_success()
                self.close()
            except FileNotFoundError as e:
                print(f"-----ERROR: {e} ---")
                self.setWindowTitle(str(e))
            except Exception as e:
                print(f"-----ERROR: {e} ---")
                self.setWindowTitle(f"Error loading project: {e}")

        self.progress = ProgressWindow(
            message="Loading project...",
            duration=1000,
            on_complete=after_progress
        )
        self.progress.show()

    def load_existing_project(self, project_tag):
        """Wrapper for SceneProject().load_existing to make testing easier."""
        return self.sp.load_existing(project_tag)

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def closeEvent(self, event):
        self.on_cancel()
        event.accept()


# Run stand-alone for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec_())
