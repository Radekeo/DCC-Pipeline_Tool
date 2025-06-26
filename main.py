import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QDialog
# from adapters.maya_adapter import export_selected_to_alembic
import maya.standalone
import maya.cmds as cmds

maya.standalone.initialize(name='PipelineTool')

# Load a fixed test file (update path as needed)
scene_path = "./data/sample/scene/ball_anim.mb"
cmds.file(scene_path, o=True, f=True)
start_frame = cmds.playbackOptions(q=True, min=True)
end_frame = cmds.playbackOptions(q=True, max=True)
frame_count = int(end_frame - start_frame + 1)


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PySide2 Demo Window")
        self.setGeometry(100, 100, 300, 150)

        # Create a label and a button
        self.label = QLabel("Hello, World!", self)
        self.button = QPushButton("Click Me", self)

        # Connect button click to function
        self.button.clicked.connect(self.on_button_click)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def on_button_click(self):
        self.new_frame = FrameWindow()
        self.new_frame.show()
        # self.label.setText("Button Clicked!")
        
class FrameWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frames")
        self.resize(100,100)

        layout = QVBoxLayout()
        label = QLabel()
        label.setText(f"Total Frames: {frame_count}")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)
        

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec_())
