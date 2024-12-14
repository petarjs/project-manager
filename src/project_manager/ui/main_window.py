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

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        
        self.title("Project Manager")
        self.geometry("1000x600")
        
        # Initialize services
        self.project_service = ProjectService()
        self.script_service = ScriptService()
        
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
        
        logger.debug("Window initialized")

    def run(self) -> None:
        """Start the application."""
        self.mainloop() 