from PySide2.QtCore import QObject, Signal, QRunnable, Slot
from core.projects import SceneProject

class ProjectCreationWorkerSignals(QObject):
    finished = Signal(dict)  # Pass the result or metadata if needed
    error = Signal(str)

class ProjectCreationWorker(QRunnable):
    def __init__(self, project_name, file_path, file_type):
        super().__init__()
        self.project_name = project_name
        self.file_path = file_path
        self.file_type = file_type
        self.signals = ProjectCreationWorkerSignals()

    @Slot()
    def run(self):
        try:
            sp = SceneProject()
            sp.create_new(self.project_name, self.file_path, self.file_type)
            self.signals.finished.emit(sp.metadata)
        except Exception as e:
            self.signals.error.emit(str(e))
