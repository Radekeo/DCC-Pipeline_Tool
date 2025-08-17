import pytest
from PySide2.QtWidgets import QApplication

@pytest.fixture(scope="session")
def app():
    """Global QApplication instance shared across all tests."""
    return QApplication.instance() or QApplication([])
