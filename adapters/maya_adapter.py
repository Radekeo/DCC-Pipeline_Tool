import maya.cmds as cmds
import os
from core.assets import register_new_asset

def export_selected_to_alembic(project_root, asset_name):
    selected = cmds.ls(selection=True)
    if not selected:
        cmds.warning("No objects selected for export.")
        return

    version_path, export_path = register_new_asset(project_root, asset_name, f\"{asset_name}.abc\")

    job_str = f\"-frameRange 1 1 -dataFormat ogawa -root {selected[0]} -file {export_path}\"
    cmds.AbcExport(j=job_str)
    print(f\"Exported: {export_path}\")
