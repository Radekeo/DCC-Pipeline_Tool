import hou
import sys
from pathlib import Path

class HoudiniAdapter:
    def __init__(self,usd_scene):
        hou.hipFile.clear(suppress_save_prompt=True)
        self.file_name = usd_scene
        self.name = Path(self.file_name).stem
        self.scene = Path("data/sample/scene") / self.file_name
        self.scene = str(self.scene.resolve())
        self.stage = hou.node("/stage") or hou.node("/").createNode("stage")
        
    def import_usd_to_stage(self):
        print(f"SCENE PATH IS : {self.scene}")
        # export_scene = Path(self.file_name).with_suffix(".hipnc")
        # export_path = Path("data/sample/assets") / export_scene
        # export_path = str(export_path.resolve())
        
        # Create USD import
        usd_sublayer = self.stage.createNode("sublayer", node_name="usd_layer")

        usd_sublayer.parm("filepath1").set(self.scene)



        message1 = f"[HOUDINI] Imported USD and saved to stage"
        
        # Setup for rendering(move when UI is developed)
        # Path set up        
        # Create new folder path
        render_output_path = Path("data/sample/renders") / self.name

        # Make the folder
        render_output_path.mkdir(parents=True, exist_ok=True)
        render_output_path = str(render_output_path.resolve())

        print(f"Folder created: {render_output_path}")

        message2 = self.render(usd_sublayer, output_path=render_output_path, frame_range=(1,30))
        return message1, message2

    # def render(self, file_path):
    #     message = "RENDERING"
    #     return message
    
    def render(self, usd_scene, output_path="renders/", renderer="karma", frame_range=(1, 1)):
        # Create a render settings node (karma render settings)
        karma = self.stage.createNode("karma", "karma_settings")
        karma.setInput(0, usd_scene)
        karma.parm("picture").set(f"{output_path}/{self.name}_$F4.exr")

        # Create new USD Render ROP
        usd_render_rop = self.stage.createNode("usdrender_rop", "usd_render_rop")
        usd_render_rop.setInput(0, karma)  # connect to Karma
        
        # render_rop.parm("lopoutput").set(f"{output_path}/output.usd")
        # render_rop.parm("rendersettings").set(settings.path())
        usd_render_rop.parm("trange").set(1)  # render frame range

        # Delete Key Frames
        usd_render_rop.parm("f1").deleteAllKeyframes()
        usd_render_rop.parm("f2").deleteAllKeyframes()

        # Set Frame Range
        usd_render_rop.parm("f1").set(frame_range[0])
        usd_render_rop.parm("f2").set(frame_range[1])
        usd_render_rop.parm("f3").set(1)  # step
        
        
        # Flatten stage into single usd
        # Parameter template for 'savestyle'
        # pt = render_rop.parm("savestyle").parmTemplate().menuItems()
        # flatten = pt[3]

        # render_rop.parm("savestyle").set(flatten)

        usd_render_rop.render()

        return f"[HOUDINI] Rendered frames {frame_range[0]} - {frame_range[1]} to {output_path}"


if __name__ == "__main__":
    print("HOUDINI IS RUNNING")
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
