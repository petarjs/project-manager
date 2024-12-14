import logging
import multiprocessing
from pathlib import Path

from .services.project_service import ProjectService
from .services.script_service import ScriptService
from .ui.status_bar import ProjectManagerStatusBar
from .ui.window_manager import start_window


def main() -> None:
    """Run the application."""
    # Configure multiprocessing to use 'spawn' on macOS
    multiprocessing.set_start_method('spawn')
    
    # Set up logging to show only INFO and above by default
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    # Enable debug logging only for specific modules
    logging.getLogger('project_manager.ui').setLevel(logging.DEBUG)
    
    logger = logging.getLogger(__name__)
    
    logger.info("Starting application...")
    try:
        # Start window process
        window_process = multiprocessing.Process(target=start_window)
        window_process.start()
        logger.debug(f"Started window process with PID: {window_process.pid}")
        
        # Initialize services for status bar
        project_service = ProjectService()
        script_service = ScriptService()
        
        # Create and run status bar app
        app = ProjectManagerStatusBar(project_service, script_service)
        logger.debug("Created status bar app")
        
        # This will block and run the app
        logger.debug("Starting status bar app...")
        app.run()
        
        # Clean up window process when app exits
        if window_process.is_alive():
            window_process.terminate()
            window_process.join(timeout=5)
        
        logger.debug("Application finished")
    except Exception as e:
        logger.error("Error running application", exc_info=True)
        raise


if __name__ == "__main__":
    main() 