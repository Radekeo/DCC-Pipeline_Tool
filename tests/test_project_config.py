import pytest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from core.project import ProjectConfig, DEFAULT_USER, ROOT_DIR

@pytest.fixture
def mock_project_config(tmp_path):
    # Use a temporary directory for project_dir
    project_dir = tmp_path / "TestProject"
    project_dir.mkdir()
    return ProjectConfig("TestProject", str(project_dir), ["scene1.usd"])

def test_initialization_sets_data(tmp_path):
    project_dir = tmp_path / "TestProject"
    project_dir.mkdir()
    
    with patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()) as m_open, \
         patch("core.project.yaml.dump") as mock_yaml_dump:
        
        pc = ProjectConfig("TestProject", str(project_dir), ["scene1.usd"])

        # Ensure attributes set
        assert pc.project_name == "TestProject"
        assert pc.scene_files == ["scene1.usd"]
        assert pc.data["created_by"] == DEFAULT_USER
        assert pc.data["root_dir"] == ROOT_DIR

        # Ensure os.makedirs called for config_dir
        mock_makedirs.assert_called_with(pc.config_dir)
        # Ensure YAML was saved
        mock_yaml_dump.assert_called()

def test_add_shot_calls_save(mock_project_config):
    pc = mock_project_config
    with patch.object(pc, "save") as mock_save:
        pc.add_shot("Shot001", (1, 10))
        assert "Shot001" in pc.data["shots"]
        assert pc.data["shot_struct"]["Shot001"] == (1, 10)
        mock_save.assert_called_once()

def test_remove_shot_calls_save(mock_project_config):
    pc = mock_project_config
    pc.data["shots"] = ["Shot001"]
    pc.data["shot_struct"] = {"Shot001": (1, 10)}
    pc.data["renders"] = {"rsv001": ["Shot001_rf1"]}
    
    with patch.object(pc, "save") as mock_save:
        pc.remove_shot("Shot001")
        assert "Shot001" not in pc.data["shots"]
        assert "Shot001" not in pc.data["shot_struct"]
        # Render entries for that shot removed
        assert pc.data["renders"]["rsv001"] == []
        mock_save.assert_called_once()

def test_add_render_setting_initializes_renders(mock_project_config):
    pc = mock_project_config
    with patch.object(pc, "save") as mock_save:
        settings = {"output_format": "png"}
        pc.add_render_setting("rsv_test", settings)
        assert pc.data["renderSettings"]["rsv_test"]["output_format"] == "png"
        assert "rsv_test" in pc.data["renders"]
        assert pc.data["renders"]["rsv_test"] == []
        mock_save.assert_called_once()

def test_add_render_appends_frame(mock_project_config):
    pc = mock_project_config
    with patch.object(pc, "save") as mock_save:
        pc.add_render("rsv_test2", "rf1v001")
        assert "rf1v001" in pc.data["renders"]["rsv_test2"]
        mock_save.assert_called_once()

def test_load_returns_yaml_data(mock_project_config):
    pc = mock_project_config
    mock_yaml_data = {"shots": ["ShotX"]}

    with patch("builtins.open", mock_open(read_data="data")) as m_open, \
         patch("core.project.yaml.safe_load", return_value=mock_yaml_data):
        path, data = pc.load()
        assert path == pc.yaml_path
        assert data == mock_yaml_data

def test_save_calls_yaml_dump(mock_project_config):
    pc = mock_project_config

    with patch("builtins.open", mock_open()) as m_open, \
         patch("core.project.yaml.dump") as mock_yaml_dump:
        pc.save()
        # YAML dump should be called with data and file handle
        mock_yaml_dump.assert_called()
