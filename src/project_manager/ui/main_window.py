import tkinter as tk
from tkinter import ttk
import logging

from .components.projects_list import ProjectsList
from .components.new_project import NewProjectForm
from ..services.project_service import ProjectService
from ..services.script_service import ScriptService

logger = logging.getLogger(__name__)

class MainWindow(tk.Tk):
    """Main application window."""

    def __init__(
        self,
        project_service: ProjectService,
        script_service: ScriptService
    ) -> None:
        """Initialize the main window.
        
        Args:
            project_service: Project service instance
            script_service: Script service instance
        """
        logger.debug("Initializing MainWindow")
        super().__init__()
        
        self.title("Project Manager")
        self.geometry("1000x600")
        
        # Store services
        self.project_service = project_service
        self.script_service = script_service
        
        # Make sure window appears on top
        self.attributes('-topmost', True)  # Make window stay on top
        self.update()  # Force an update
        self.attributes('-topmost', False)  # Allow window to go back
        
        # Create main container with padding
        main_container = ttk.Frame(self, padding="10")
        main_container.pack(fill='both', expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create components
        self.projects_list = ProjectsList(
            self.notebook,
            self.project_service,
            self.script_service
        )
        self.notebook.add(self.projects_list.frame, text='Projects')
        
        self.new_project = NewProjectForm(
            self.notebook,
            self.project_service,
            self.script_service,
            self.projects_list.load_projects
        )
        self.notebook.add(self.new_project.frame, text='New Project')
        
        logger.debug("Window initialized and configured")

    def run(self) -> None:
        """Start the application."""
        self.mainloop() 