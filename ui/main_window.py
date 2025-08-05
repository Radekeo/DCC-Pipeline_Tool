import sys
import os
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QDialog
import subprocess


MAYAPY = "/usr/autodesk/maya2023/bin/mayapy"
HYTHON = "/opt/hfs20.5.332/bin/hython3.11"

class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pipeline Tool")
        self.setGeometry(100, 100, 300, 150)

        # Create a label and a button
        self.label = QLabel("Start Project", self)
        self.button = QPushButton("Run", self)

        # Connect button click to function
        self.button.clicked.connect(self.on_button_click)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def on_button_click(self):
        maya_usd_export = subprocess.run(
            [
                MAYAPY,
                "adapters/maya_adapter.py",
                "export_usd",
                "--file", "gallery.mb",
                "--startf", "1",
                "--endf", "100"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # output to string
        )

        for line in maya_usd_export.stdout.splitlines():
            if line.startswith("[MAYA]"):
                message = line
                break
        
        self.new_frame = FrameWindow(message)
        self.new_frame.show()
        
        # self.label.setText("Button Clicked!") #debugging
        
class FrameWindow(QDialog):
    def __init__(self, message):
    # def __init__(self):
        super().__init__()
        self.setWindowTitle("Frames")
        self.resize(100,100)
        self.message = message

        self.button = QPushButton("Hou", self)

        # Connect button click to function
        self.button.clicked.connect(self.on_button_click)

        layout = QVBoxLayout()
        label = QLabel()
        label.setText("Done")
        label.setText(self.message)
        # label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def on_button_click(self):
        # print("RUNNING HOUDINI subprocess...")
        houdini_usd_to_stage = subprocess.run(
            [
                HYTHON,
                "adapters/houdini.py",
                "import_usd_to_stage",
                "--file", "gallery.usda",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # output to string
        )
        print("STDOUT:")
        print(houdini_usd_to_stage.stdout)

        print("STDERR:")
        print(houdini_usd_to_stage.stderr)
        # for line in houdini_usd_to_stage.stdout.splitlines():
        #     if line.startswith("[HOUDINI]"):
        #         self.message = line
        #         break
        
        
        

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec_())
