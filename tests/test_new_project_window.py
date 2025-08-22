import sys
import pytest
from unittest.mock import patch, MagicMock
from PySide2.QtWidgets import QApplication
from ui.start_window import NewProjectWindow

@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture
def window():
    """Fresh NewProjectWindow for each test."""
    return NewProjectWindow(on_cancel=lambda: None, on_success=lambda: None)

import pytest
from unittest.mock import MagicMock, patch

def test_create_project_success(window):
    window.name_input.setText("TestProject")
    window.file_display.setText("/path/to/file.usda")

    # Mock SceneProject instance
    mock_scene_project = MagicMock()
    mock_scene_project.create_new = MagicMock(return_value=None)
    mock_scene_project.config = MagicMock()
    mock_scene_project.config.load.return_value = ("mock_metadata_file.yaml", {"shots": []})

    with patch("ui.start_window.SceneProject", return_value=mock_scene_project):
        with patch("ui.start_window.ProgressWindow") as mock_progress:
            def side_effect(message, duration, on_complete):
                on_complete()
                return MagicMock()
            mock_progress.side_effect = side_effect

            window.create_project()

            assert window.error_label.text() == ""
            mock_scene_project.create_new.assert_called_once_with(
                "TestProject", "/path/to/file.usda", "usd"
            )



def test_create_project_missing_name(window):
    """Should show error when name is missing."""
    window.name_input.setText("")
    window.file_display.setText("/path/to/file.usda")

    with patch("core.project.SceneProject.create_new") as mock_create:
        window.create_project()
        assert "required" in window.error_label.text().lower()
        mock_create.assert_not_called()

def test_create_project_missing_file(window):
    """Should show error when file is missing."""
    window.name_input.setText("TestProject")
    window.file_display.setText("")

    with patch("core.project.SceneProject.create_new") as mock_create:
        window.create_project()
        assert "required" in window.error_label.text().lower()
        mock_create.assert_not_called()
