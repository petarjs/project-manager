import tkinter as tk
from tkinter import ttk, messagebox
import logging

from .base import BaseComponent
from ...services.project_service import ProjectService
from ...services.script_service import ScriptService

logger = logging.getLogger(__name__)

class NewProjectForm(BaseComponent):
    """New project creation form."""

    def __init__(
        self, 
        parent: tk.Widget, 
        project_service: ProjectService,
        script_service: ScriptService,
        on_project_created: callable
    ) -> None:
        """Initialize the new project form."""
        super().__init__(parent)
        self.project_service = project_service
        self.script_service = script_service
        self.on_project_created = on_project_created
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the component UI."""
        # Create form
        form = ttk.Frame(self.frame)
        form.pack(padx=20, pady=20)
        
        # Project name
        ttk.Label(form, text="Project Name:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.name_entry = ttk.Entry(form, width=40)
        self.name_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Display name
        ttk.Label(form, text="Display Name:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.pretty_name_entry = ttk.Entry(form, width=40)
        self.pretty_name_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Create button
        ttk.Button(form, text="Create Project", command=self._create_project).grid(
            row=2, column=0, columnspan=2, pady=20
        )
        
        # Output area
        self.output_text = tk.Text(self.frame, height=10, width=60)
        self.output_text.pack(padx=20, pady=10, fill='both', expand=True)

    def _create_project(self) -> None:
        """Handle project creation."""
        name = self.name_entry.get().strip()
        pretty_name = self.pretty_name_entry.get().strip()
        
        if not name or not pretty_name:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Clear output
        self.output_text.delete(1.0, tk.END)
        
        def output_callback(line: str) -> None:
            """Callback to handle script output."""
            self.output_text.insert(tk.END, f"{line}\n")
            self.output_text.see(tk.END)  # Scroll to bottom
            self.output_text.update()  # Force update
        
        try:
            # Get next available port and Redis DB
            port = self.project_service._get_next_port()
            redis_db = self.project_service._get_next_redis_db()
            
            # Execute script with output callback
            success = self.script_service.execute_new_project_script(
                name,
                pretty_name,
                port,
                redis_db,
                output_callback
            )
            
            if success:
                # Clear form fields
                self.name_entry.delete(0, tk.END)
                self.pretty_name_entry.delete(0, tk.END)
                
                # Reload projects from filesystem
                self.project_service._load_projects()
                
                messagebox.showinfo("Success", "Project created successfully!")
                self.on_project_created()  # Refresh projects list
            else:
                messagebox.showerror("Error", "Failed to create project")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e)) 