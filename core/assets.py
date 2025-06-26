import os
from core.utils import read_json, write_json, get_next_version, ensure_dir

def register_new_asset(project_root, asset_name, file_name):
    index_path = os.path.join(project_root, "pipeline_data", "index.json")
    data = read_json(index_path)

    if asset_name not in data:
        data[asset_name] = {"versions": []}

    asset_path = os.path.join(project_root, "assets", asset_name)
    ensure_dir(asset_path)
    new_version = get_next_version(asset_path)
    version_path = os.path.join(asset_path, new_version)
    ensure_dir(version_path)

    data[asset_name]["versions"].append(new_version)
    data[asset_name]["latest"] = new_version
    write_json(index_path, data)

    return version_path, os.path.join(version_path, file_name)
