# adapters/houdini_adapter.py
import argparse
from pathlib import Path
import hou


def ensure_stage():
    stage = hou.node("/stage")
    if stage is None:
        stage = hou.node("/").createNode("stage")
    return stage


def load_usd_as_sublayer(stage, usd_path: str):
    sub = stage.createNode("sublayer", node_name="usd_layer")
    sub.parm("filepath1").set(usd_path)
    return sub


def karma_chain_with_lights(sublayer, output_file: str, width: int, height: int, camera: str = None,
                            light: str = None):
    """
    Build Karma LOP chain with optional dome or physical sky light.
    Lights exist but are bypassed by default. User can activate one.
    """
    parent = sublayer.parent()

    # Dome light
    dome = parent.createNode("domelight::3.0", "dome_light")
    dome.setFirstInput(sublayer)
    dome.bypass(True)

    # Physical sky
    sky = parent.createNode("karmaphysicalsky", "sky_light")
    sky.setFirstInput(dome)
    sky.bypass(True)

    # Activate selected light
    if light == "Dome Light":
        dome.bypass(False)
    elif light == "Physical Sky":
        sky.bypass(False)

    # Karma node
    karma = parent.createNode("karma", "karma_settings")
    karma.setFirstInput(sky)

    # Resolution override
    if karma.parm("resoverride"):
        karma.parm("resoverride").set(1)
    if karma.parm("resx"):
        karma.parm("resx").set(width)
    if karma.parm("resy"):
        karma.parm("resy").set(height)

    # Set camera
    if camera:
        karma.parm("camera").set(camera)
    else:
        # fallback to first camera in stage
        karma.parm("camera").set("camera1")

    # Output path
    if karma.parm("picture"):
        karma.parm("picture").set(output_file)

    # USD Render ROP
    rop = parent.createNode("usdrender_rop", "usd_render_rop")
    rop.setFirstInput(karma)
    return rop


def render_with_karma(usd_path: str, output_file: str, frame: int, width: int = 1920,
                      height: int = 1080, camera: str = None, light: str = None):
    """
    Full render helper:
    - Loads USD as sublayer
    - Builds Karma + light chain
    - Renders single frame
    """
    stage = ensure_stage()
    sub = load_usd_as_sublayer(stage, usd_path)
    rop = karma_chain_with_lights(sub, output_file, width, height, camera, light)

    # Render current frame
    hou.setFrame(frame)
    if rop.parm("trange"):
        rop.parm("trange").set(0)
    rop.render()
    return f"[HOUDINI] Rendered frame {frame} → {output_file}"


def cli():
    p = argparse.ArgumentParser(description="Houdini Karma Adapter")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render-frame")
    r.add_argument("--scene", required=True, help="Absolute path to USD scene")
    r.add_argument("--output", required=True, help="Absolute output file (.exr)")
    r.add_argument("--frame", type=int, required=True)
    r.add_argument("--width", type=int, default=1920)
    r.add_argument("--height", type=int, default=1080)
    r.add_argument("--camera", type=str, default=None, help="Camera name in USD to use")
    r.add_argument("--light", type=str, default=None, choices=["Dome Light", "Physical Sky"],
                   help="Optional light to enable")

    args = p.parse_args()
    print(f"!!!!!!LIGHT IS {args.light} AND CAMERA IS {args.camera}!!!!!!")

    if args.cmd == "render-frame":
        msg = render_with_karma(
            usd_path=str(Path(args.scene).resolve()),
            output_file=str(Path(args.output).resolve()),
            frame=args.frame,
            width=args.width,
            height=args.height,
            camera=args.camera,
            light=args.light,
        )
        print(msg)


if __name__ == "__main__":
    cli()
