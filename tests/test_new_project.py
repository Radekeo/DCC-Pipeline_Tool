# tests/test_new_project.py
import os
import pytest

from core.utils import check_file_type


# --- Unit tests for pure logic ---
@pytest.mark.parametrize("filename, expected", [
    ("scene.usda", "usd"),
    ("scene.usdc", "usd"),
    ("scene.ma", "maya"),
    ("scene.mb", "maya"),
    ("scene.hip", "houdini"),
    ("scene.hipnc", "houdini"),
    ("scene.txt", None),
])

def test_check_file_type(filename, expected):
    assert check_file_type(filename) == expected