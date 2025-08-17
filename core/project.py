import os
import shutil
from datetime import datetime
import yaml
from pathlib import Path
import logging


from core.utils import convert_to_usd

DEFAULT_USER = "ADMIN"
ROOT_DIR = "TEMP"  # Can be changed later to a shared or network path

class SceneProject:
    def __init__(self):
        os.makedirs(ROOT_DIR, exist_ok=True)
        self.project_path = None
        self.metadata = {}

    def create_new(self, project_name, file_path, file_type):
        # --- Validate ---
        project_dir = os.path.join(ROOT_DIR, project_name)
        if os.path.exists(project_dir):
            raise FileExistsError(f"Project '{project_name}' already exists.")

        os.makedirs(project_dir)

        # --- Create folder structure ---
        render_dir = os.path.join(project_dir, "Renders")
        # config_dir = os.path.join(project_dir, "Config")
        os.makedirs(render_dir)
        # os.makedirs(config_dir)

        # --- Copy or convert scene file ---
        if file_type in ["maya", "houdini"]:
            convert_to_usd(project_name, file_path, file_type)
            scene_file = str(Path((project_name).lower()).with_suffix(".usda"))

        else:
            scene_file = os.path.basename(file_path)
            dest_scene_path = os.path.join(project_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_scene_path)

        self.project_path = project_dir
        # self._setup_logging(self.project_path)
        # --- Initialize ProjectConfig ---
        self.config = ProjectConfig(project_name, project_dir, scene_file)

        print(f"New project '{project_name}' created at '{self.project_path}'.")

    
    def load_existing(self, project_tag):
        project_name = project_tag.lstrip("@")
        project_dir = os.path.join(ROOT_DIR, project_name)
        config_path = os.path.join(project_dir, "Config", "metadata.yaml")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"No project found with tag '{project_tag}'.")

        with open(config_path, "r") as f:
            self.metadata = yaml.safe_load(f)

        self.project_path = project_dir
        print(f"Loaded project '{self.metadata['project_name']}' from '{project_dir}'.")
        return self.metadata

    def _setup_logging(self, project_dir):
        log_file = os.path.join(project_dir, "Config", "project.log")
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        # Avoid duplicate handlers when reopening project
        if not self.logger.handlers:
            self.logger.addHandler(handler)

        self.logger.info("Logging initialized for project at %s", project_dir)


class ProjectConfig:
    def __init__(self, project_name, project_dir, scene=None):
        self.project_name = project_name
        self.project_dir = project_dir
        self.scene_file = scene
        self.config_dir = os.path.join(self.project_dir, "Config")
        self.yaml_path = os.path.join(self.config_dir, "metadata.yaml")
        self.data = {
            "project_name": self.project_name,
            "project_tag" : f"@{self.project_name}",
            "scene_file": self.scene_file,
            "project_dir": project_dir,
            "shots": [],
            "shot_struct": {},
            "renderSettings": {},
            "renders": {},
            "created_by": DEFAULT_USER,
            "created_at": datetime.now().isoformat(),
            "root_dir": ROOT_DIR
        }

        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)        
        if os.path.exists(self.yaml_path):
            self.load()
        else:
            self.save()

    def load(self):
        with open(self.yaml_path, "r") as f:
            self.data = yaml.safe_load(f) or self.data
        return self.data

    def save(self):
        with open(self.yaml_path, "w") as f:
            yaml.dump(self.data, f)

    # --- Shots ---
    def add_shot(self, shot_name, frame_range):
        if shot_name not in self.data["shots"]:
            self.data["shots"].append(shot_name)
        self.data["shot_struct"][shot_name] = frame_range
        self.save()

    def remove_shot(self, shot_name):
        if shot_name in self.data["shots"]:
            self.data["shots"].remove(shot_name)
        self.data["shot_struct"].pop(shot_name, None)
        # Remove any renders for this shot
        for rsv, frames in self.data["renders"].items():
            self.data["renders"][rsv] = [f for f in frames if not f.startswith(shot_name)]
        self.save()

    # --- Render Settings ---
    def add_render_setting(self, rsv_name, settings_dict):
        self.data["renderSettings"][rsv_name] = settings_dict
        if rsv_name not in self.data["renders"]:
            self.data["renders"][rsv_name] = []
        self.save()

    # --- Record Renders ---
    def add_render(self, rsv_name, frame_id):
        if rsv_name not in self.data["renders"]:
            self.data["renders"][rsv_name] = []
        self.data["renders"][rsv_name].append(frame_id)
        self.save()