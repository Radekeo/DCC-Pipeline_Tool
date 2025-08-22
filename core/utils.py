import sys
import os
import subprocess
from pathlib import Path
import yaml

from pxr import Usd, UsdGeom

from core.models import Project, Shot, RenderSettingsVersion, FrameVersion


MAYAPY = "/opt/autodesk/maya2023/bin/mayapy"
HYTHON = "/opt/hfs20.5.332/bin/hython3.11"
ROOT_DIR = "TEMP"

def check_file_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".usda", ".usdc"]:
        return "usd"
    elif ext in [".ma", ".mb"]:
        return "maya"
    elif ext in [".hip", ".hipnc"]:
        return "houdini"
    return None

def convert_to_usd(project_name, file_path, file_type):
    print(f">>> convert_to_usd(project={project_name}, file={file_path}, type={file_type})")

    file_path = str(Path(file_path).resolve())
    new_scene_file = f"{Path(file_path).stem}.usda"

    # put the USD into the Project/Scene folder (so downstream code finds it)
    export_dir = Path(ROOT_DIR) / project_name / "Scene"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = str((export_dir / new_scene_file).resolve())

    if file_type == "maya":
        # resolve absolute path to the adapter script
        script = (Path(__file__).resolve().parents[1] / "adapters" / "maya_adapter.py").resolve()

        cmd = [
            MAYAPY,
            str(script),
            "export_usd",
            "--directory", str(Path(ROOT_DIR).resolve()),
            "--scene", project_name,
            "--file", file_path,
            "--outputf", export_path,
            "--startf", "1",
            "--endf", "100",
        ]

        print(">>> Running MAYAPY:", " ".join(cmd))
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # show both streams to actually see failures
        print(">>> MAYAPY STDOUT:\n", result.stdout)
        print(">>> MAYAPY STDERR:\n", result.stderr)

        if result.returncode != 0:
            raise RuntimeError(f"mayapy failed (code {result.returncode}). See STDERR above.")

        # optional: extract a friendly line
        for line in result.stdout.splitlines():
            if line.startswith("[MAYA]"):
                print(line)
                break

    return new_scene_file, export_path

def get_default_render_path(project_path: str):
    """
    Returns the default Renders folder for a given project.
    """
    render_path = Path(project_path) / "Renders"
    render_path.mkdir(parents=True, exist_ok=True)
    return render_path

def save_project_to_yaml(project: Project, filepath: str):
    with open(filepath, "w") as f:
        yaml.dump(project.__dict__, f, sort_keys=False)

def load_project_from_yaml(filepath: str) -> Project:
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return Project(**data)

def list_cameras_in_usd(usd_path: str):
    """
    Returns a list of camera paths in the USD file.
    """
    stage = Usd.Stage.Open(usd_path)
    if not stage:
        return []
    cameras = [prim.GetPath().pathString for prim in stage.Traverse() if prim.IsA(UsdGeom.Camera)]
    return cameras

def run_git_command(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Git error: {result.stderr}")
    return result.stdout.strip()

def init_repo_with_lfs(path):
    if not os.path.exists(os.path.join(path, ".git")):
        run_git_command("git init", cwd=path)
        run_git_command("git lfs install", cwd=path)
        run_git_command('git lfs track "renders/*"', cwd=path)
        run_git_command("git add .gitattributes", cwd=path)
        run_git_command('git commit -m "Initial LFS setup"', cwd=path)

def commit_and_push(path, message):
    run_git_command("git add .", cwd=path)
    run_git_command(f'git commit -m "{message}"', cwd=path)
    run_git_command("git push", cwd=path)

def clone_repo(repo_url, dest_path):
    run_git_command(f"git clone {repo_url} {dest_path}")

