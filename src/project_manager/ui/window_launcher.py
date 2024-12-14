
import sys
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from project_manager.services.project_service import ProjectService
from project_manager.services.script_service import ScriptService
from project_manager.ui.main_window import MainWindow

logging.basicConfig(level=logging.DEBUG)

def main():
    project_service = ProjectService()
    script_service = ScriptService()
    window = MainWindow(project_service, script_service)
    window.run()

if __name__ == "__main__":
    main()
