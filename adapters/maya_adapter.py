# adapters/maya_adapter.py
#!/usr/bin/env mayapy
import sys
import traceback
from pathlib import Path
import os

# Now safe to import Maya
import maya.standalone
import maya.cmds as cmds

def _ensure_usd_plugin():
    # Try both known plugin names
    if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
        try:
            cmds.loadPlugin("mayaUsdPlugin")
        except RuntimeError:
            cmds.loadPlugin("mayaUsd")

def _ensure_arnold_plugin():
    if not cmds.pluginInfo("mtoa", query=True, loaded=True):
        try:
            cmds.loadPlugin("mtoa")
            print("[INFO] Arnold (mtoa) plugin loaded")
        except RuntimeError:
            raise RuntimeError("Could not load Arnold plugin (mtoa). Please check installation.")

def export_usd(scene_file, export_file, startf, endf):
    # Open the Maya scene
    cmds.file(scene_file, o=True, force=True)

    # Ensure the plugin is loaded
    # if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
    #     cmds.loadPlugin("mayaUsdPlugin")
    _ensure_usd_plugin()

    # Select everything
    cmds.select(allDagObjects=True)

    # The exact options string you copied from the Script Editor
    options_str = (
        "exportUVs=1;"
        "exportSkels=none;"
        "exportSkin=none;"
        "exportBlendShapes=0;"
        "exportDisplayColor=1;"
        "exportColorSets=1;"
        "exportComponentTags=1;"
        "defaultMeshScheme=none;"
        "animation=1;"
        "eulerFilter=0;"
        "staticSingleSample=0;"
        f"startTime={startf};"
        f"endTime={endf};"
        "frameStride=1;"
        "frameSample=0.0;"
        "defaultUSDFormat=usda;"
        "parentScope=;"
        "shadingMode=useRegistry;"
        "convertMaterialsTo=[MaterialX];"
        "exportInstances=1;"
        "exportVisibility=1;"
        "mergeTransformAndShape=1;"
        "stripNamespaces=0;"
        "materialsScopeName=mtl"
    )

    # Call the USD exporter with those options
    cmds.file(
        export_file,
        force=True,
        options=options_str,
        type="USD Export",
        pr=True,
        ea=True  # export all
    )

    return f"[MAYA] Exported USD to {export_file}"

def render(scene_file, output_path, startf, endf, ext, camera="persp"):
    """
    Render the scene using Arnold.

    Args:
        output_path (str): Where to save rendered images.
        frame_range (tuple): (start_frame, end_frame).
        camera (str): Camera to render from.
    """
    # Load scene
    cmds.file(scene_file, o=True, force=True)

    # Load Arnold plugin
    _ensure_arnold_plugin()

    # Set Arnold as the current renderer
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

    # Output settings
    cmds.setAttr("defaultArnoldDriver.ai_translator", ext, type="string")  # PNG output
    cmds.setAttr("defaultArnoldDriver.pre", output_path, type="string")       # Output directory
    cmds.setAttr("defaultArnoldDriver.mergeAOVs", 1)                         # Single file per frame

    # Frame range
    cmds.setAttr("defaultRenderGlobals.startFrame", startf)
    cmds.setAttr("defaultRenderGlobals.endFrame", endf)
    cmds.setAttr("defaultRenderGlobals.animation", 1 if endf > startf else 0)

    # Render
    try:
        cmds.arnoldRender(seq=True, camera=camera)
    except Exception as e:
        print(f"[MAYA] ERROR: Arnold render failed - {e}")
        return f"[MAYA] ERROR: Arnold render failed - {e}"
        
    print(f"[MAYA] Rendered frames {startf}-{endf} to {output_path}")
    return f"[MAYA] Rendered frames {startf}-{endf} to {output_path}"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Maya Adapter CLI")
    parser.add_argument("function", choices=["export_usd", "render"])
    parser.add_argument("--directory", default="TEMP")  # not used here but kept to match your call
    parser.add_argument("--scene", required=True, help="Project name")
    parser.add_argument("--file", required=True, help=".ma/.mb scene full path")
    parser.add_argument("--startf", type=int, default=1)
    parser.add_argument("--endf", type=int, default=1)
    parser.add_argument("--outputf", help="USD export full path")
    parser.add_argument("--outputr", help="Render output path (unused here)")
    parser.add_argument("--ext", choices=["png", "exr", "jpeg"])
    parser.add_argument("--cam", default="cam1")

    args = parser.parse_args()

    try:
        maya.standalone.initialize(name='python')

        if args.function == "export_usd":
            if not args.outputf:
                print("[MAYA] ERROR: --outputf is required for export_usd", file=sys.stderr)
                sys.exit(2)
            export_usd(args.file, args.outputf, args.startf, args.endf)

        elif args.function == "render":
            if not args.outputr:
                print("[MAYA] ERROR: --outputr is required for export_usd", file=sys.stderr)
                sys.exit(2)
            render(args.file, args.outputr, args.startf, args.endf, args.ext, args.cam)

    except Exception:
        traceback.print_exc()
        print("[MAYA] ERROR: Export failed", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            maya.standalone.uninitialize()
        except Exception:
            pass

if __name__ == "__main__":
    main()
