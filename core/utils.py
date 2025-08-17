import sys
import os
import subprocess
from pathlib import Path
import yaml

from core.models import Project, Shot, RenderSettingsVersion, FrameVersion


MAYAPY = "/usr/autodesk/maya2023/bin/mayapy"
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
    
    # os.makedirs(ROOT_DIR, exist_ok=True)

    if file_type == "maya":

        maya_usd_export = subprocess.run(
            [
                MAYAPY,
                "adapters/maya_adapter.py",
                "export_usd",
                "--directory", f"{ROOT_DIR}",
                "--scene", f"{project_name}",
                "--file", f"{file_path}",
                "--startf", "1",
                "--endf", "100"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        text=True  # output to string
        )

        for line in maya_usd_export.stdout.splitlines():
            if line.startswith("[MAYA]"):
                message = line
                break

        print(message)

    export_path = f"{ROOT_DIR}/{project_name}/{project_name}.usd"

    # return export_path
        
def save_project_to_yaml(project: Project, filepath: str):
    with open(filepath, "w") as f:
        yaml.dump(project.__dict__, f, sort_keys=False)

def load_project_from_yaml(filepath: str) -> Project:
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return Project(**data)

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




# def ensure_dir(path):
#     Path(path).mkdir(parents=True, exist_ok=True)

# def get_next_version(path):
#     versions = [d for d in os.listdir(path) if d.startswith("v") and d[1:].isdigit()]
#     if not versions:
#         return "v001"
#     versions.sort()
#     last = versions[-1]
#     next_ver = int(last[1:]) + 1
#     return f"v{next_ver:03d}"

# def write_json(filepath, data):
#     with open(filepath, 'w') as f:
#         json.dump(data, f, indent=4)

# def read_json(filepath):
#     if not os.path.exists(filepath):
#         return {}
#     with open(filepath, 'r') as f:
#         return json.load(f)
