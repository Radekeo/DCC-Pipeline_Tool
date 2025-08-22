# core/rendering.py
import os
import yaml
import subprocess
from datetime import datetime
from pathlib import Path

# from adapters.nuke_adapter import NukeAdapter   # keep if you need it

DEFAULT_FILENAME_TEMPLATE = "{shot}_{camera}_{frame}"
SUPPORTED_RENDERERS = ["Arnold", "Karma"]
MIN_FPS = 1
MAX_FPS = 240
MAYAPY = "/usr/autodesk/maya2023/bin/mayapy"
HYTHON = "/opt/hfs20.5.332/bin/hython3.11"


class RenderSettings:
    def __init__(
        self,
        renderer: str,
        fps: int,
        output_dir: str,
        output_format: str = "EXR",
        resolution_width: int = 1920,
        resolution_height: int = 1080,
        motion_blur: bool = False,
        denoise: bool = False,
        filename_template: str = DEFAULT_FILENAME_TEMPLATE,
    ):
        self.renderer = renderer
        self.fps = fps
        self.output_dir = Path(output_dir)
        self.output_format = output_format
        self.resolution_width = resolution_width
        self.resolution_height = resolution_height
        self.motion_blur = motion_blur
        self.denoise = denoise
        self.filename_template = filename_template
        self.validate()

    def validate(self):
        if self.renderer not in SUPPORTED_RENDERERS:
            raise ValueError(f"Renderer '{self.renderer}' not supported. Choose from {SUPPORTED_RENDERERS}.")
        if not (MIN_FPS <= self.fps <= MAX_FPS):
            raise ValueError(f"FPS must be between {MIN_FPS} and {MAX_FPS}. Got {self.fps}.")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return True

    def generate_filename(self, shot: str, camera: str, frame: int):
        return self.filename_template.format(shot=shot, camera=camera, frame=frame)


class Renderer:
    """
    Renderer now supports Karma via hython subprocess.
    Give it metadata + rsv so it can find the scene and compute versioned filenames.
    """
    def __init__(self, settings: RenderSettings, metadata: dict | None = None, rsv: str | None = None, hython: str = "hython"):
        self.settings = settings
        self.metadata = metadata or {}
        self.rsv = rsv
        # self.hython = hython  # path to hython; ensure it's on PATH or provide absolute

    # --- Public API used by your UI loop ---
    def render_shot(self, shot_info: dict):
        if self.settings.renderer == "Karma":
            return self._render_karma_frame(shot_info)
        elif self.settings.renderer == "Arnold":
            return self._render_arnold_frame(shot_info)
        else:
            # Stub for Arnold/Renderman until implemented
            filename = self.settings.generate_filename(**shot_info)
            filepath = self.settings.output_dir / filename
            print(f"[Renderer] (stub) {self.settings.renderer} rendering {filename}")
            return filepath


    # --- Internal helpers ---
    def _scene_abs_path(self, renderer: str) -> Path:
        """
        Resolve the correct scene file for the renderer.

        Args:
            renderer: "Arnold" or "Karma"

        Returns:
            Absolute Path to the scene file
        """
        proj_dir = Path(self.metadata.get("project_dir", "")).resolve()
        scene_files = self.metadata.get("scene_file", [])

        if not isinstance(scene_files, list) or not scene_files:
            raise ValueError("metadata['scene_file'] must be a non-empty list of filenames")

        # Directory where scene files are stored
        scenes_dir = proj_dir / "Scene"

        # Choose file based on renderer
        if renderer == "Arnold":
            # Prefer Maya file if available
            maya_files = [f for f in scene_files if f.lower().endswith((".ma", ".mb"))]
            if not maya_files:
                raise ValueError("No Maya scene file (.ma or .mb) found for Arnold rendering")
            chosen_file = maya_files[0]
        elif renderer == "Karma":
            usd_files = [f for f in scene_files if f.lower().endswith(".usda")]
            if not usd_files:
                raise ValueError("No USD scene file (.usd) found for Karma rendering")
            chosen_file = usd_files[0]
        else:
            raise ValueError(f"Unknown renderer: {renderer}")

        scene_path = scenes_dir / chosen_file
        if not scene_path.exists():
            raise FileNotFoundError(f"Scene file not found: {scene_path}")

        return scene_path.resolve()

    def _render_output_dir(self) -> Path:
        """
        Store frames under: {settings.output_dir}/{rsv}/
        """
        if self.rsv:
            out = self.settings.output_dir / self.rsv
        else:
            out = self.settings.output_dir
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _rf_filename(self, frame: int) -> str:
        """
        rf{frame}v{version}.{ext}  → rf1v001.exr
        """
        ver = self._version_from_rsv()
        ext = self.settings.output_format.lower()
        return f"rf{frame}v{ver:03d}.{ext}"

    def _version_from_rsv(self) -> int:
        """
        Extract version number from self.rsv (e.g. "rsv003" → 3).
        Defaults to 1 if missing or malformed.
        """
        if not self.rsv or not self.rsv.startswith("rsv"):
            return 1
        try:
            return int(self.rsv.replace("rsv", ""))
        except ValueError:
            return 1

    def _render_arnold_frame(self, shot_info: dict):
        """
        Launch mayapy → adapters/maya_adapter.py render
        """
        frame = int(shot_info.get("frame", 1))
        scene = self._scene_abs_path("Arnold")
        extension = self.settings.output_format.lower()
        out_dir = self._render_output_dir()  # reuse directory logic; could rename to _arnold_output_dir
        out_file = out_dir / self._rf_filename(frame)

        cmd = [
            MAYAPY,
            str(Path("adapters/maya_adapter.py").resolve()),
            "render",
            "--file", str(scene),
            "--scene", self.metadata.get('project_name'),
            "--outputr", str(out_file),
            "--startf", str(frame),
            "--endf", str(frame),
            "--ext", extension
        ]

        # print("[Renderer] Arnold subprocess:", " ".join(cmd))
        # Raises exception if mayapy fails
        subprocess.run(cmd, check=True)

        return out_file


    def _render_karma_frame(self, shot_info: dict):
        """
        Launch hython → adapters/houdini_adapter.py render-frame
        """
        frame = int(shot_info.get("frame", 1))
        scene = self._scene_abs_path("Karma")
        out_dir = self._render_output_dir()
        out_file = out_dir / self._rf_filename(frame)

        cmd = [
            HYTHON,
            str(Path("adapters/houdini_adapter.py").resolve()),
            "render-frame",
            "--scene", str(scene),
            "--output", str(out_file),
            "--frame", str(frame),
            "--width", str(self.settings.resolution_width),
            "--height", str(self.settings.resolution_height),
            "--camera", self.settings.camera,
            "--light", self.settings.light,
        ]

        print("[Renderer] Karma subprocess:", " ".join(cmd))
        # Raise if hython fails
        subprocess.run(cmd, check=True)

        return out_file


class RenderManager:
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                self.data = yaml.safe_load(f) or {}
        else:
            self.data = {}
        if "renders" not in self.data:
            self.data["renders"] = {}

    def _save(self):
        with open(self.yaml_path, "w") as f:
            yaml.safe_dump(self.data, f)

    def _next_render_version(self):
        existing = self.data.get("renders", {})
        versions = [int(k.replace("rsv", "")) for k in existing.keys() if k.startswith("rsv")]
        return f"rsv{max(versions, default=0)+1:03d}"

    def new_render_version(self, settings: RenderSettings) -> str:
        rsv = self._next_render_version()
        settings_dict = {k: str(v) if isinstance(v, Path) else v for k, v in settings.__dict__.items()}
        self.data["renders"][rsv] = {
            "settings": settings_dict,
            "frames": []
        }
        self._save()
        return rsv

    def update_frame(self, rsv, frame_number):
        if rsv not in self.data["renders"]:
            raise ValueError(f"Render version {rsv} not found.")
        if frame_number not in self.data["renders"][rsv]["frames"]:
            self.data["renders"][rsv]["frames"].append(frame_number)
            self.data["renders"][rsv]["frames"].sort()
            self._save()

    def get_render_versions(self):
        return sorted(self.data["renders"].keys())

    def get_frames(self, rsv):
        if rsv not in self.data["renders"]:
            raise ValueError(f"Render version {rsv} not found.")
        return self.data["renders"][rsv]["frames"]

    def get_render_info(self, rsv):
        if rsv not in self.data["renders"]:
            raise ValueError(f"Render version {rsv} not found.")
        return self.data["renders"][rsv]
