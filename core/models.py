from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class Shot:
    id: str
    frame_range: Tuple[int, int]

@dataclass
class RenderSettingsVersion:
    id: str
    settings: Dict
    frames: List[int]

@dataclass
class FrameVersion:
    frame_number: int
    version_number: int
    render_settings_id: str
    output_path: str

@dataclass
class Project:
    name: str
    tag: str
    shots: List[Shot] = field(default_factory=list)
    render_settings_versions: List[RenderSettingsVersion] = field(default_factory=list)
    frame_versions: List[FrameVersion] = field(default_factory=list)
