import pytest
from unittest.mock import patch
from ui.start_window import ExistingProjectWindow
from PySide2.QtWidgets import QApplication

# Ensure a QApplication exists for the tests
app = QApplication.instance() or QApplication([])

@pytest.fixture
def window():
    return ExistingProjectWindow(on_cancel=lambda: None, on_success=lambda: None)

def test_load_project_success(window):
    """Should load an existing project and pass metadata_file to MainProjectWindow."""
    window.tag_input.setText("@MyProject")

    mock_metadata = {"project_dir": "/mock/project"}

    with patch("core.project.SceneProject.load_existing", return_value=mock_metadata) as mock_load, \
         patch("ui.start_window.MainProjectWindow") as mock_main:

        window.load_project()
        window.progress.on_complete()  # simulate progress finish

        # Ensure load_existing was called with the project tag
        mock_load.assert_called_once_with("@MyProject")

        # Build expected config path from mock_metadata
        expected_config_path = "/mock/project/Config/metadata.yaml"

        # MainProjectWindow should receive metadata_file
        mock_main.assert_called_once_with(metadata_file=expected_config_path)


def test_load_project_missing_tag(window):
    window.tag_input.setText("")
    window.load_project()
    assert window.windowTitle() == "Enter a project tag!"

def test_load_project_file_not_found(window):
    window.tag_input.setText("@MissingProject")

    with patch("core.project.SceneProject.load_existing", side_effect=FileNotFoundError("Project not found")):
        window.load_project()
        window.progress.on_complete()

    assert window.windowTitle() == "Project not found"

def test_load_project_generic_error(window):
    window.tag_input.setText("@BadProject")

    with patch("core.project.SceneProject.load_existing", side_effect=Exception("Something broke")):
        window.load_project()
        window.progress.on_complete()

    assert "Error loading project: Something broke" in window.windowTitle()
