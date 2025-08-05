import hou
import sys
from pathlib import Path

class HoudiniAdapter:
    def __init__(self,usd_scene):
        self.name = "_ha_"
        self.file_name = usd_scene
        self.scene = Path("data/sample/scene") / self.file_name
        self.scene = str(self.scene.resolve())
        
    def import_usd_to_stage(self):
        print(f"SCENE PATH IS : {self.scene}")
        export_scene = Path(self.file_name).with_suffix(".hipnc")
        export_path = Path("data/sample/assets") / export_scene
        export_path = str(export_path.resolve())
        
        # Create SOP-level USD import
        obj = hou.node("/obj") or hou.node("/").createNode("obj")
        geo = obj.createNode("geo", node_name="usd_geo")

        for c in geo.children():
            c.destroy()

        usd_import_sop = geo.createNode("usdimport", "import_usd_scene")
        usd_import_sop.parm("filepath1").set(self.scene)
        geo.layoutChildren()

        # SOP import into LOP stage
        stage = hou.node("/stage") or hou.node("/").createNode("stage")

        sop_import = stage.createNode("sopimport", "sop_import_from_usd_geo")
        sop_import.parm("soppath").set("/obj/usd_geo/import_usd_scene")
        # sop_import.parm("primpath").set("/root")

        # save the scene
        hou.hipFile.save(export_path)

        stage.layoutChildren()

        message1 = f"[HOUDINI] Imported USD and saved to {export_path}"
        
        # Setup for rendering(move when UI is developed)
        # Path set up
        new_folder = Path(export_scene).stem
        # Create new folder path
        render_output_path = Path("data/sample/renders") / new_folder

        # Make the folder
        render_output_path.mkdir(parents=True, exist_ok=True)
        render_output_path = str(render_output_path.resolve())

        print(f"Folder created: {render_output_path}")

        message2 = self.render(file_path=export_path, output_path=render_output_path, frame_range=(1,5))
        return message1, message2

    # def render(self, file_path):
    #     message = "RENDERING"
    #     return message
    
    def render(self, file_path, output_path="renders/", renderer="karma", frame_range=(1, 1)):
        # import os

        # Load HIP file
        hou.hipFile.load(file_path)

        # Get stage context
        stage = hou.node("/stage")
        if not stage:
            raise RuntimeError("No /stage node found in scene.")

        # Render product node
        render_product = stage.createNode("renderproduct", "render_product")
        # render_product.setInput(0, settings)
        render_product.parm("productName").set("beauty")
        render_product.parm("productType").set("color")

        # Render Var(AOV)
        render_var = stage.createNode("rendervar", "beauty_aov")
        render_var.setInput(0, render_product)
        render_var.parm("sourceName").set("Ci")  # Beauty pass

        # Create a render node to execute
        usd_import_sop = hou.node("/obj/usd_geo/import_usd_scene")
        usd_import_lop = hou.node("/stage/sop_import_from_usd_geo")

        #   Prevent automatic layer saving
        # if usd_import_sop.parm("outputfile"):
        #     usd_import_sop.parm("outputfile").set("")
        if usd_import_sop.parm("enableoutputpath"):
            usd_import_sop.parm("enableoutputpath").set(False)
    

        render_rop = stage.createNode("usd_rop", "usd_render")
        render_rop.setInput(0, usd_import_lop)
        render_rop.parm("lopoutput").set(f"{output_path}/output.usd")
        # render_rop.parm("rendersettings").set(settings.path())
        render_rop.parm("trange").set(1)  # render frame range
        render_rop.parm("f1").set(frame_range[0])
        render_rop.parm("f2").set(frame_range[1])
        render_rop.parm("f3").set(1)  # step

        # Create a render settings node (karma render settings)
        settings = stage.createNode("karma", "karma_settings")
        settings.parm("picture").set(f"{output_path}/render_$F4.exr")
        
        # Flatten stage into single usd
        # Parameter template for 'savestyle'
        pt = render_rop.parm("savestyle").parmTemplate().menuItems()
        flatten = pt[3]

        render_rop.parm("savestyle").set(flatten)

        render_rop.render()

        return f"[HOUDINI] Rendered frames {frame_range[0]} - {frame_range[1]} to {output_path}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Houdini Adapter CLI")
    parser.add_argument("function", choices=["import_usd_to_stage", "render"])
    parser.add_argument("--file", required=True, help="Scene file name, e.g., scene.usda")
    
    # parser.add_argument("--output", help="Hip output path")

    args = parser.parse_args()
    adapter = HoudiniAdapter(args.file)

    if args.function == "import_usd_to_stage":
        print(adapter.import_usd_to_stage())
    elif args.function == "render":
        if not args.output:
            raise ValueError("Render function requires --output path.")
        print(adapter.render(args.output))
