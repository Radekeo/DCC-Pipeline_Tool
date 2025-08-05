# export_usd_maya.py

import maya.standalone
import maya.cmds as cmds

from pathlib import Path

class MayaAdapter:
    def __init__(self, file_name):
        self.file_name = file_name
        self.scene = f"data/sample/scene/{file_name}"
        maya.standalone.initialize(name='python')

    def export_usd(self, frame_range):
        # Open the Maya scene
        export_scene = Path(self.file_name).with_suffix(".usda")
        export_path = f"data/sample/scene/{export_scene}"
        cmds.file(self.scene, o=True, force=True)

        # Ensure plugin is loaded
        if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
            cmds.loadPlugin("mayaUsdPlugin")

        # Select everything for export
        cmds.select(allDagObjects=True)
        
        # Export to USD
        cmds.file(
            export_path,
            force=True,
            options=f"exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportColorSets=1;exportVisibility=1;startTime={frame_range[0]};endTime={frame_range[1]};",
            typ="USD Export",
            pr=True,
            es=True
        )
        message = f"[MAYA] Exported USD to {export_path}"
        return message

    def render(self, file_path):
        message = "RENDERING"
        return message

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Maya Adapter CLI")
    parser.add_argument("function", choices=["export_usd", "render"])
    parser.add_argument("--file", required=True, help="Scene file name, e.g., scene.mb")
    parser.add_argument("--startf", type=int, default=1)
    parser.add_argument("--endf", type=int, default=100)
    parser.add_argument("--output", help="Render output path")

    args = parser.parse_args()
    adapter = MayaAdapter(args.file)

    if args.function == "export_usd":
        print(adapter.export_usd((args.startf, args.endf)))
    elif args.function == "render":
        if not args.output:
            raise ValueError("Render function requires --output path.")
        print(adapter.render(args.output))
