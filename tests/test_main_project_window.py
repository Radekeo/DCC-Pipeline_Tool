import os
import pytest
import yaml

from PySide2.QtWidgets import QApplication
from PySide2.QtTest import QTest
from PySide2.QtCore import Qt

from ui.project_window import MainProjectWindow, ManageShotsWindow


@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_metadata(tmp_path):
    data = {
        "project_name": "TestProject",
        "project_dir": str(tmp_path),
        "scene_file": "scene.usd",
        "shots": ["ShotA"],
        "shot_struct": {"ShotA": [1, 5]},
    }
    file_path = tmp_path / "metadata.yaml"
    with open(file_path, "w") as f:
        yaml.safe_dump(data, f)
    return file_path, data


def test_project_structure_loads(app, sample_metadata):
    file_path, data = sample_metadata
    window = MainProjectWindow(metadata_file=str(file_path))
    structure = window.get_project_structure_dict()

    assert structure[0]["name"] == "Shots"
    assert structure[0]["children"][0]["name"] == "ShotA"
    assert len(structure[0]["children"][0]["children"]) == 5  # 5 frames


def test_open_manage_shots(app, sample_metadata):
    file_path, _ = sample_metadata
    window = MainProjectWindow(metadata_file=str(file_path))

    window.open_manage_shots()
    assert isinstance(window.shots_manager, ManageShotsWindow)


def test_add_shot_updates_metadata(app, sample_metadata):
    file_path, _ = sample_metadata
    window = MainProjectWindow(metadata_file=str(file_path))
    shots_win = ManageShotsWindow(window)

    # Fill inputs
    QTest.keyClicks(shots_win.shot_name_input, "ShotB")
    QTest.keyClicks(shots_win.range_input, "10-20")

    # Click Add
    QTest.mouseClick(shots_win.add_button, Qt.LeftButton)

    # Metadata should now include ShotB
    assert "ShotB" in window.metadata["shots"]
    assert window.metadata["shot_struct"]["ShotB"] == [10, 20]

    # Project structure should refresh
    structure = window.get_project_structure_dict()
    shot_names = [c["name"] for c in structure[0]["children"]]
    assert "ShotB" in shot_names


def test_update_shot_changes_name_and_range(app, sample_metadata):
    file_path, _ = sample_metadata
    window = MainProjectWindow(metadata_file=str(file_path))
    shots_win = ManageShotsWindow(window)

    # Add a shot first
    shots_win.shot_name_input.setText("ShotB")
    shots_win.range_input.setText("10-20")
    shots_win.add_shot()

    # Select ShotB in the list
    shots_win.shot_list.setCurrentRow(1)  # index 0 is ShotA, 1 is ShotB
    shots_win.shot_name_input.setText("ShotC")
    shots_win.range_input.setText("15-25")
    shots_win.update_shot()

    assert "ShotC" in window.metadata["shots"]
    assert [15, 25] == window.metadata["shot_struct"]["ShotC"]
    assert "ShotB" not in window.metadata["shots"]


def test_delete_shot_removes_metadata(app, sample_metadata):
    file_path, _ = sample_metadata
    window = MainProjectWindow(metadata_file=str(file_path))
    shots_win = ManageShotsWindow(window)

    # Add a shot
    shots_win.shot_name_input.setText("ShotB")
    shots_win.range_input.setText("10-20")
    shots_win.add_shot()

    # Select and delete
    shots_win.shot_list.setCurrentRow(1)
    shots_win.delete_shot()

    assert "ShotB" not in window.metadata["shots"]
    assert "ShotB" not in window.metadata["shot_struct"]
