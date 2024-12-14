"""Window management module."""
import logging
import sys

from ..services.project_service import ProjectService
from ..services.script_service import ScriptService
from .main_window import MainWindow

logger = logging.getLogger(__name__)

def start_window() -> None:
    """Start the main window process."""
    try:
        project_service = ProjectService()
        script_service = ScriptService()
        window = MainWindow(project_service, script_service)
        window.run()
    except Exception as e:
        logger.error(f"Error in window process: {e}", exc_info=True)
        sys.exit(1) 