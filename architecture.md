# Directory Structure and Module Overview

## adapters/

This folder contains all integrations with eMaya and Houdini. Each adapter is responsible for abstracting the API of the respective application.

### maya_adapter.py

Handles communication and automation tasks within Autodesk Maya.

Functions include: scene export and render functions

Example function:

```
def export_usd(scene_file, export_file, startf, endf):
    """Opens a Maya scene_file and exports as export_file USD scene with MaterialX shading"""
```

```
def render(scene_file, output_path, startf, endf, ext, camera="persp"):
    """
    Render the scene using Arnold within frame range (startf,endf).
    """
```
### houdini_adapter.py

Provides Houdini-specific integration.

Functions include: Scene Import to Stage, manipulating nodes, rendering using Karma and exporting render data.

Example function:

```
def render_with_karma(usd_path: str, output_file: str, frame: int, width: int = 1920,
                      height: int = 1080, camera: str = None, light: str = None):
    """
    Full render helper:
    - Loads USD as sublayer
    - Builds Karma + light chain
    - Renders single frame
    """
```

## core/

Contains the backend logic of the application.

### project.py

Manages project data, structure, and configuration.

Handles creation, saving, loading, and validation of projects.

Key classes are:
`SceneProject` which handles the creation and loading of projects and `ProjectConfig` which creates the configuration file, and saves, loads and updates the project metadata in a `metadata.yaml` file

### rendering.py

Handles scene rendering pipelines using Karma and Arnold.

Key classes are:
```RenderSettings``` which collects and stores render settings gotten from the UI and passes to relevant functions,```Renderer```  which supports Karma via Hython  and Arnold via Mayapy and ```RenderManager``` which creates the rendering specific configuration file, and saves, loads and updates the rendering metadata in a ```renders.yaml``` file. This function also tracks and save version information

### utils.py

Helper functions and utility classes used throughout the project.

Common functions include ```check_file_type(file_path)``` which returns "Maya" or "USD" based on the scene file extension and ```list_cameras_in_usd(usd_path: str)``` which helps populate the UI with the cameras found in a scene file

## ui/

Contains all PySide2 GUI components.

### start_window.py

Entry window for starting the application and choosing actions (new project, load project).

### progress_window.py

Displays progress bars/progress status for long operations like rendering or importing scenes.

### project_window.py

Main project dashboard showing shots management, scene hierarchy, and settings.

### render_window.py

Displays render settings used to configure each render.

### render_gallery.py
Displays rendered images or viewport previews.
Project dashboard showing project assets, scene hierarchy, versions and settings per rendered asset.
Shows colour channels for images

## tests/

Contains testing and mocking functions using pytest. Test files include:

    test_existing_project.py
    test_main_project_window.py
    test_new_project_window.py
    test_new_project.py
    test_render_manager.py


Use pytest for automated testing.