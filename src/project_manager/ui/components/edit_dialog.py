import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Callable

from .base import BaseComponent
from ...models.project import Project
from ...services.project_service import ProjectService

logger = logging.getLogger(__name__)

class EditDialog(tk.Toplevel):
    """Dialog for editing project details."""

    def __init__(
        self,
        parent: tk.Widget,
        project: Project,
        project_service: ProjectService,
        on_update: Callable[[], None]
    ) -> None:
        """
        Initialize the edit dialog.
        
        Args:
            parent: Parent widget
            project: Project to edit
            project_service: ProjectService instance
            on_update: Callback to run after successful update
        """
        super().__init__(parent)
        self.title(f"Edit Project: {project.name}")
        self.project = project
        self.project_service = project_service
        self.on_update = on_update
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create form
        self._setup_ui()
        
        # Center dialog on parent
        self.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        # Create main frame with padding
        main = ttk.Frame(self, padding="10")
        main.pack(fill='both', expand=True)
        
        # Port
        ttk.Label(main, text="Port:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.port_entry = ttk.Entry(main, width=10)
        self.port_entry.insert(0, str(self.project.port))
        self.port_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Redis DB
        ttk.Label(main, text="Redis DB:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.redis_entry = ttk.Entry(main, width=10)
        self.redis_entry.insert(0, str(self.project.redis_db))
        self.redis_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Frontend URL
        ttk.Label(main, text="Frontend URL:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.fe_url_entry = ttk.Entry(main, width=40)
        self.fe_url_entry.insert(0, self.project.fe_url or '')
        self.fe_url_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # Backend URL
        ttk.Label(main, text="Backend URL:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.be_url_entry = ttk.Entry(main, width=40)
        self.be_url_entry.insert(0, self.project.be_url or '')
        self.be_url_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side='left', padx=5)
        
        # Configure grid
        main.columnconfigure(1, weight=1)

    def _save(self) -> None:
        """Save the changes."""
        try:
            # Validate and convert inputs
            port = int(self.port_entry.get().strip())
            redis_db = int(self.redis_entry.get().strip())
            fe_url = self.fe_url_entry.get().strip()
            be_url = self.be_url_entry.get().strip()
            
            # Update project
            updates = {
                'port': port,
                'redis_db': redis_db,
                'fe_url': fe_url or None,
                'be_url': be_url or None
            }
            
            self.project_service.update_project(self.project.name, updates)
            self.on_update()  # Refresh project list
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update project: {e}") 