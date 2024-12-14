import logging

from .ui.main_window import MainWindow


def main() -> None:
    """Run the application."""
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    logger.debug("Starting application...")
    try:
        app = MainWindow()
        logger.debug("Created main window")
        app.run()
        logger.debug("Application finished")
    except Exception as e:
        logger.error("Error running application", exc_info=True)
        raise


if __name__ == "__main__":
    main() 