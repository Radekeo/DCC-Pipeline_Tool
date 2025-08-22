import unittest
from core.rendering import RenderManager
from pathlib import Path

class TestRenderManager(unittest.TestCase):
    def setUp(self):
        # Initialize manager with fake path
        self.manager = RenderManager("fake_path.yaml")

        # Inject fake data to simulate renders
        self.manager.data = {
            "renders": {
                "rsv001": {"settings": {"output_dir": str(Path("/tmp")), "output_format": "png"}},
                "rsv002": {"settings": {"output_dir": str(Path("/tmp")), "output_format": "png"}},
            }
        }

    def test_get_render_versions(self):
        versions = self.manager.get_render_versions()
        self.assertEqual(versions, ["rsv001", "rsv002"])

    def test_get_render_info(self):
        info = self.manager.get_render_info("rsv001")
        self.assertIn("settings", info)
        self.assertEqual(info["settings"]["output_format"], "png")
