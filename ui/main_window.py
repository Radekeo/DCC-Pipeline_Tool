import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QComboBox

class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Render Job Settings")
        self.label = QLabel("", self)
        layout = QVBoxLayout()

        self.scene_input = QLineEdit()
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["Arnold", "Mantra"])
        self.frame_range = QLineEdit("1-100")
        self.resolution = QLineEdit("1920x1080")

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.on_button_click)


        # Layout
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

    def on_button_click(self):
        self.label.setText("Button Clicked!")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec_())
