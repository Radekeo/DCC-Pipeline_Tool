import sys
import time
import os
from PySide2.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QFileDialog
)
from PySide2.QtCore import Qt, QThread, QThreadPool

from workers import ProjectCreationWorker
from progress_window import ProgressWindow
from project_window import ProjectWindow
from core.utils import check_file_type 


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
        self.threadpool = QThreadPool()

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
        # Ensure Valid File
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Project File", "", "Scene Files (*.usda *.usdc *.ma *.mb *.hip *.hipnc)"
        )

        if not file_path:
            return

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

        # Show progress window
        self.progress = ProgressWindow(
            message="Creating project...",
            duration=0  # We will close it manually
        )
        self.progress.show()

        # Create worker
        worker = ProjectCreationWorker(project_name, file_path, file_type)
        worker.signals.finished.connect(self.on_project_created)
        worker.signals.error.connect(self.on_project_error)

        self.threadpool.start(worker)
        self.close()

    def on_project_created(self, metadata):
        self.progress.close()

        print(f"Project created: {metadata['project_name']}")
        self.project_window = ProjectWindow()
        self.project_window.show()
        self.on_success()

    def on_project_error(self, error_message):
        self.progress.close()
        self.error_label.setText(f"Error: {error_message}")
        self.error_label.show()
        self.setEnabled(True)
        self.show()

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
        self.setFixedSize(400, 100)
        self.on_cancel = on_cancel
        self.on_success = on_success

        # --- Project tag input with button beside ---
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter project tag...")

        load_button = QPushButton("Load Project")
        load_button.clicked.connect(self.load_project)

        tag_row = QHBoxLayout()
        tag_row.addWidget(self.tag_input)
        tag_row.addWidget(load_button)

        # --- Main layout ---
        layout = QVBoxLayout()
        layout.addLayout(tag_row)
        self.setLayout(layout)

    def load_project(self):
        project_tag = self.tag_input.text().strip()

        if not project_tag:
            self.setWindowTitle("Enter a project tag!")
            return

        print(f"Loading project: {project_tag}")
        # self.close()
        # self.on_success()
        def after_progress():
            self.project_window = ProjectWindow()
            self.project_window.show()
            self.on_success()
            self.close()
            # self.on_success()

        self.progress = ProgressWindow(
            message="Loading project...",
            duration=1000,
            on_complete=after_progress
        )
        self.progress.show()
        self.close()


    def closeEvent(self, event):
        self.on_cancel()
        event.accept()


# Run stand-alone for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec_())
