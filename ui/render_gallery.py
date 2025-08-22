import os
from pathlib import Path

from PySide2.QtWidgets import (
    QWidget, QSplitter, QTreeWidget, QTreeWidgetItem, QLabel,
    QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QSizePolicy,
    QScrollArea
)

from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import Qt, Signal
from PIL import Image
import numpy as np

from core.rendering import RenderManager   # your class from rendering.py


class ThumbnailWidget(QWidget):
    clicked = Signal(str, str)  # image_path, rsv

    def __init__(self, image_path: str, version_label: str, rsv: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.rsv = rsv

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(
                pixmap.scaled(120, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.image_label.setText("No Image")

        self.text_label = QLabel(version_label)
        self.text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.image_label)
        layout.addWidget(self.text_label)

        # Click handling
        self.image_label.mousePressEvent = self.on_click
        self.text_label.mousePressEvent = self.on_click

    def on_click(self, event):
        self.clicked.emit(self.image_path, self.rsv)



class RenderGallery(QWidget):
    """Middle panel: main image + version thumbnails + button group."""
    image_selected = Signal(str)  # emits the current main image path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.current_image_path = None
        self.current_rsv = None
        self.current_channel = None  # None, "R","G","B"

        # Main image
        self.main_image_label = QLabel("No image")
        self.main_image_label.setAlignment(Qt.AlignCenter)
        self.main_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.main_image_label)

        # Button row
        btn_row = QHBoxLayout()
        self.btn1 = QPushButton("Channel R")
        self.btn2 = QPushButton("Channel G")
        self.btn3 = QPushButton("Channel B")
        btn_row.addWidget(self.btn1)
        btn_row.addWidget(self.btn2)
        btn_row.addWidget(self.btn3)
        self.layout.addLayout(btn_row)

        self.btn1.clicked.connect(lambda: self.show_channel("R"))
        self.btn2.clicked.connect(lambda: self.show_channel("G"))
        self.btn3.clicked.connect(lambda: self.show_channel("B"))

        # Scroll area for version thumbnails
        self.thumb_scroll = QScrollArea()
        self.thumb_scroll.setWidgetResizable(True)
        self.thumb_container = QWidget()
        self.thumb_layout = QHBoxLayout(self.thumb_container)
        self.thumb_scroll.setWidget(self.thumb_container)
        self.layout.addWidget(self.thumb_scroll)

    # ---------- public API ----------
    def clear_gallery(self):
        """Reset viewer and thumbnails."""
        self.main_image_label.setText("No image")
        self.current_image_path = None
        self.current_rsv = None
        self.current_channel = None
        while self.thumb_layout.count():
            child = self.thumb_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def set_main_image(self, path: str, rsv: str = None):
        """Show an image as the main viewer; rsv optional (derived from folder if omitted)."""
        if not os.path.exists(path):
            self.main_image_label.setText("Image not found")
            return
        self.current_image_path = path
        self.current_rsv = rsv or Path(path).parent.name
        self.current_channel = None  # reset channel view
        self._update_view()
        self.image_selected.emit(path)  # notify parent window

    def add_version_thumb(self, path: str, rsv: str, version_label: str):
        """Add a labeled, clickable thumbnail."""
        if not os.path.exists(path):
            return
        tw = ThumbnailWidget(path, version_label, rsv)
        tw.clicked.connect(self._on_thumb_clicked)
        self.thumb_layout.addWidget(tw)

    def show_channel(self, channel: str):
        """Set current channel (R/G/B) and update the main image view."""
        if not self.current_image_path:
            return
        self.current_channel = channel
        self._update_view()

    # ---------- internals ----------
    def _on_thumb_clicked(self, path: str, rsv: str):
        """Swap clicked thumb with main image (and keep versions labeled)."""
        prev_main = self.current_image_path
        prev_rsv = self.current_rsv

        # Remove the clicked thumb widget
        sender = self.sender()
        if isinstance(sender, QWidget):
            sender.setParent(None)
            sender.deleteLater()

        # Set new main
        self.set_main_image(path, rsv)

        # Add the previous main as a thumbnail (if existed)
        if prev_main:
            self.add_version_thumb(prev_main, prev_rsv, self._version_label_from_path(prev_main))

    def _version_label_from_path(self, path: str) -> str:
        stem = Path(path).stem  # e.g. rf1v003
        # find trailing v### if present
        if 'v' in stem:
            try:
                ver = int(stem.split('v')[-1])
                return f"v{ver:03d}"
            except ValueError:
                pass
        return "v?"

    def _update_view(self):
        """Update the main image label based on channel or original."""
        try:
            img = Image.open(self.current_image_path).convert("RGB")

            if self.current_channel:
                # Use the selected channel as a single-band grayscale image
                idx = {"R": 0, "G": 1, "B": 2}[self.current_channel]
                channel_data = img.getchannel(idx)
                img = channel_data.convert("L")

            img_qt = self.pil2pixmap(img)
            self.main_image_label.setPixmap(img_qt.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            print("Error showing image:", e)
            self.main_image_label.setText("Error showing image")

    @staticmethod
    def pil2pixmap(im: Image.Image) -> QPixmap:
        """Convert PIL Image to QPixmap"""
        if im.mode == "RGB":
            data = im.tobytes("raw", "RGB")
            qimg = QImage(data, im.size[0], im.size[1], QImage.Format_RGB888)
        elif im.mode == "L":
            data = im.tobytes("raw", "L")
            qimg = QImage(data, im.size[0], im.size[1], QImage.Format_Grayscale8)
        else:
            im = im.convert("RGB")
            data = im.tobytes("raw", "RGB")
            qimg = QImage(data, im.size[0], im.size[1], QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)



class ManageShotsWindow3Panel(QWidget):
    """Full 3-panel window."""
    def __init__(self, main_window):
        super().__init__()
        self.metadata = main_window.metadata
        self.project_dir = main_window.project_path
        self.render_config_path = os.path.join(self.project_dir, "Config", "renders.yaml")
        self.manager = RenderManager(self.render_config_path)

        self.setWindowTitle("View Project")
        self.resize(1400, 800)

        splitter = QSplitter(Qt.Horizontal, self)
        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        # Left panel: shots tree
        self.shot_tree = QTreeWidget()
        self.shot_tree.setHeaderLabels(["Shot / Frame"])
        splitter.addWidget(self.shot_tree)

        # Middle panel: gallery
        self.render_gallery = RenderGallery()
        splitter.addWidget(self.render_gallery)

        # Right panel: render settings
        self.settings_form = QFormLayout()
        self.settings_widget = QWidget()
        self.settings_widget.setLayout(self.settings_form)
        splitter.addWidget(self.settings_widget)

        splitter.setSizes([300, 800, 300])

        # Populate
        self.populate_shots()

        # Connections
        self.shot_tree.itemClicked.connect(self.on_item_clicked)
        self.render_gallery.image_selected.connect(self.show_render_settings)

    def populate_shots(self):
        shot_struct = self.metadata.get("shot_struct", {})
        for shot_name, frames in shot_struct.items():
            shot_item = QTreeWidgetItem([shot_name])
            self.shot_tree.addTopLevelItem(shot_item)
            if isinstance(frames, (list, tuple)) and len(frames) == 2:
                for i in range(frames[0], frames[1] + 1):
                    frame_item = QTreeWidgetItem([f"Frame {i}"])
                    shot_item.addChild(frame_item)

    def on_item_clicked(self, item, column):
        try:
            text = item.text(0)
            parent = item.parent()
            if parent:  # frame item
                shot_name = parent.text(0)
                frame_number = int(text.replace("Frame ", ""))
                self.load_gallery(shot_name, frame_number)
        except Exception as e:
            print("Exception in on_item_clicked:", e)

    def load_gallery(self, shot_name: str, frame_number: int):
        self.render_gallery.clear_gallery()
        try:
            versions = self.manager.get_render_versions()
            if not versions:
                self.render_gallery.main_image_label.setText("No renders yet")
                return

            frame_files = []

            # Collect all files for this frame from all render folders
            for rsv in versions:
                info = self.manager.get_render_info(rsv)
                ext = info["settings"].get("output_format", "png").lower()
                output_dir = Path(info["settings"]["output_dir"])
                render_folder = output_dir / rsv
                if not render_folder.exists():
                    continue

                # rf{frame}v*.ext
                for file in render_folder.glob(f"rf{frame_number}v*.{ext}"):
                    frame_files.append(file)

            if not frame_files:
                self.render_gallery.main_image_label.setText("No render for this frame yet")
                return

            # Sort by version (v001 → v002 → ... )
            frame_files.sort(key=lambda f: int(f.stem.split('v')[-1]))

            # Latest version = main image
            latest = frame_files[-1]
            latest_rsv = latest.parent.name
            self.render_gallery.set_main_image(str(latest), latest_rsv)

            # Older versions = labeled, clickable thumbnails
            for f in reversed(frame_files[:-1]):  # newest older first, left→right
                rsv = f.parent.name
                ver_label = f"v{int(f.stem.split('v')[-1]):03d}"
                self.render_gallery.add_version_thumb(str(f), rsv, ver_label)

        except Exception as e:
            print("Exception in load_gallery:", e)
            self.render_gallery.main_image_label.setText("Error loading renders")


    def show_render_settings(self, image_path: str):
        # Clear existing rows
        while self.settings_form.count():
            item = self.settings_form.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            rsv = Path(image_path).parent.name  # assume parent folder = rsvxxx
            info = self.manager.get_render_info(rsv)
            for key, value in info["settings"].items():
                self.settings_form.addRow(QLabel(key), QLabel(str(value)))
        except Exception as e:
            print("Exception in show_render_settings:", e)