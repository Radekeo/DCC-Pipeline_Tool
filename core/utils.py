import os
import json
from pathlib import Path

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def get_next_version(path):
    versions = [d for d in os.listdir(path) if d.startswith("v") and d[1:].isdigit()]
    if not versions:
        return "v001"
    versions.sort()
    last = versions[-1]
    next_ver = int(last[1:]) + 1
    return f"v{next_ver:03d}"

def write_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def read_json(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)
