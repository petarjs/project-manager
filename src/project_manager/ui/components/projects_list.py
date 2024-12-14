import tkinter as tk
from tkinter import ttk, messagebox
import logging
import webbrowser
import subprocess
from typing import Optional
from pathlib import Path

from .base import BaseComponent
from .toast import Toast
from ...models.project import Project
from ...services.project_service import ProjectService
from ...services.script_service import ScriptService

logger = logging.getLogger(__name__)

class ProjectsList(BaseComponent):
    """Projects list component with actions."""

    def __init__(
        self, 
        parent: tk.Widget, 
        project_service: ProjectService,
        script_service: ScriptService
    ) -> None:
        """Initialize the projects list.
        
        Args:
            parent: Parent widget
            project_service: Project service instance
            script_service: Script service instance
        """
        super().__init__(parent)
        self.project_service = project_service
        self.script_service = script_service
        self.toast = Toast(self.frame)
        self._setup_ui()
        self.load_projects()

    def _setup_ui(self) -> None:
        """Set up the component UI."""
        # Create main container with scrollbar
        self.canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Add refresh button at the top
        refresh_frame = ttk.Frame(self.frame)
        refresh_frame.pack(fill='x', padx=5, pady=5)
        
        refresh_btn = ttk.Button(
            refresh_frame,
            text="↻ Refresh",
            command=self._refresh_projects
        )
        refresh_btn.pack(side='right')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configure column weights to control stretching
        self.scrollable_frame.grid_columnconfigure(0, weight=2)  # Name
        self.scrollable_frame.grid_columnconfigure(1, weight=3)  # Display Name
        self.scrollable_frame.grid_columnconfigure(2, weight=1)  # Port
        self.scrollable_frame.grid_columnconfigure(3, weight=1)  # Redis DB
        self.scrollable_frame.grid_columnconfigure(4, weight=2)  # Actions
        
        # Create headers
        style = ttk.Style()
        style.configure("Header.TLabel", font=('Arial', 10, 'bold'))
        
        ttk.Label(self.scrollable_frame, text="Name", style="Header.TLabel").grid(
            row=0, column=0, padx=5, pady=5, sticky='ew'
        )
        ttk.Label(self.scrollable_frame, text="Display Name", style="Header.TLabel").grid(
            row=0, column=1, padx=5, pady=5, sticky='ew'
        )
        ttk.Label(self.scrollable_frame, text="Port", style="Header.TLabel").grid(
            row=0, column=2, padx=5, pady=5, sticky='ew'
        )
        ttk.Label(self.scrollable_frame, text="Redis DB", style="Header.TLabel").grid(
            row=0, column=3, padx=5, pady=5, sticky='ew'
        )
        ttk.Label(self.scrollable_frame, text="Actions", style="Header.TLabel").grid(
            row=0, column=4, padx=5, pady=5, sticky='ew'
        )
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_row(self, row_num: int, project: Project) -> None:
        """Create a row in the projects list."""
        # Project name
        ttk.Label(self.scrollable_frame, text=project.name).grid(
            row=row_num, column=0, padx=5, pady=5, sticky='ew'
        )
        
        # Display name
        ttk.Label(self.scrollable_frame, text=project.pretty_name).grid(
            row=row_num, column=1, padx=5, pady=5, sticky='ew'
        )
        
        # Port
        ttk.Label(self.scrollable_frame, text=str(project.port)).grid(
            row=row_num, column=2, padx=5, pady=5, sticky='ew'
        )
        
        # Redis DB
        ttk.Label(self.scrollable_frame, text=str(project.redis_db or '')).grid(
            row=row_num, column=3, padx=5, pady=5, sticky='ew'
        )
        
        # Actions
        actions_frame = ttk.Frame(self.scrollable_frame)
        actions_frame.grid(row=row_num, column=4, padx=5, pady=5, sticky='ew')
        
        # Frontend process button
        fe_button_text = "Stop FE" if project.fe_process_pid else "Start FE"
        fe_button = ttk.Button(
            actions_frame,
            text=fe_button_text,
            width=8,
            command=lambda p=project: self._toggle_frontend_process(p)
        )
        fe_button.pack(side='left', padx=2)
        
        # URLs
        if project.fe_url:
            ttk.Button(
                actions_frame, text="FE", width=4, style="Action.TButton",
                command=lambda: webbrowser.open(project.fe_url)
            ).pack(side='left', padx=2)
        
        if project.be_url:
            ttk.Button(
                actions_frame, text="BE", width=4, style="Action.TButton",
                command=lambda: webbrowser.open(project.be_url)
            ).pack(side='left', padx=2)
        
        ttk.Button(
            actions_frame, text="IDE", width=4, style="Action.TButton",
            command=lambda: self._open_in_cursor(project.name)
        ).pack(side='left', padx=2)
        
        ttk.Button(
            actions_frame, text="Edit", width=4, style="Action.TButton",
            command=lambda: self._edit_project(project.name)
        ).pack(side='left', padx=2)

        ttk.Button(
            actions_frame, text="🗑️", width=3, style="Delete.TButton",
            command=lambda: self._delete_project(project.name)
        ).pack(side='left', padx=2)
        
    def _toggle_frontend_process(self, project: Project) -> None:
        """Toggle the frontend process for a project."""
        if project.fe_process_pid:
            # Stop the process
            try:
                import psutil
                if psutil.pid_exists(project.fe_process_pid):
                    process = psutil.Process(project.fe_process_pid)
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        process.kill()
                
                # Update project
                self.project_service.update_project(project.name, {"fe_process_pid": None})
                logger.info(f"Stopped frontend process for {project.name}")
            except Exception as e:
                logger.error(f"Error stopping frontend process: {e}")
        else:
            # Start the process
            try:
                # Find the frontend directory
                project_dir = Path(project.directory)
                fe_dir = None
                
                # Check possible frontend locations
                fe_locations = [
                    project_dir / "www",
                    project_dir / "app",
                    project_dir / f"{project.name}-app"
                ]
                
                for location in fe_locations:
                    if location.exists() and (location / "package.json").exists():
                        fe_dir = location
                        break
                
                if not fe_dir:
                    logger.error(f"Could not find frontend directory for {project.name}")
                    return
                
                # Start the process
                process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd=str(fe_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    start_new_session=True  # This ensures the process is in its own session
                )
                
                # Update project
                self.project_service.update_project(project.name, {"fe_process_pid": process.pid})
                logger.info(f"Started frontend process for {project.name} with PID {process.pid}")
                
                # Start a thread to read output
                import threading
                
                def log_output(pipe, level):
                    for line in pipe:
                        line = line.strip()
                        if line:
                            logger.log(level, f"{project.name} FE: {line}")
                
                threading.Thread(
                    target=log_output,
                    args=(process.stdout, logging.INFO),
                    daemon=True
                ).start()
                
                threading.Thread(
                    target=log_output,
                    args=(process.stderr, logging.ERROR),
                    daemon=True
                ).start()
                
            except Exception as e:
                logger.error(f"Error starting frontend process: {e}")
        
        # Refresh list to update button text
        self.load_projects()

    def _delete_project(self, project_name: str) -> None:
        """Delete a project after confirmation."""
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the project '{project_name}'?\n\n"
            "This will:\n"
            "- Delete the project directory\n"
            "- Delete GitHub repositories\n"
            "- Drop the database\n"
            "- Remove Herd proxies\n\n"
            "This action cannot be undone!"
        ):
            return

        # Create a dialog to show deletion progress
        dialog = tk.Toplevel(self.frame)
        dialog.title("Deleting Project")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("500x300")
        dialog_x = self.frame.winfo_rootx() + (self.frame.winfo_width() // 2) - (500 // 2)
        dialog_y = self.frame.winfo_rooty() + (self.frame.winfo_height() // 2) - (300 // 2)
        dialog.geometry(f"+{dialog_x}+{dialog_y}")
        
        # Add output text widget
        output_text = tk.Text(dialog, height=15, width=60)
        output_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        def output_callback(line: str) -> None:
            """Handle script output."""
            output_text.insert(tk.END, f"{line}\n")
            output_text.see(tk.END)
            output_text.update()
        
        def close_dialog() -> None:
            """Close the dialog and refresh projects."""
            dialog.destroy()
            # Reload projects from filesystem
            self.project_service._load_projects()
            self.load_projects()  # Refresh the projects list
            # Show toast notification
            self.toast.show("Project deleted successfully")
        
        # Start deletion process
        success = self.script_service.delete_project(
            project_name,
            output_callback
        )
        
        if success:
            # Add close button
            ttk.Button(
                dialog,
                text="Close",
                command=close_dialog
            ).pack(pady=10)
        else:
            # Add close button with error state
            ttk.Button(
                dialog,
                text="Close (Error occurred)",
                command=close_dialog,
                style="Danger.TButton"
            ).pack(pady=10)

    def load_projects(self) -> None:
        """Load projects into the table."""
        # Clear existing rows
        for widget in self.scrollable_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:  # Skip headers
                widget.destroy()
        
        # Add projects
        for i, project in enumerate(self.project_service.projects, start=1):
            self._create_row(i, project)

    def _get_project(self, name: str) -> Optional[Project]:
        """Get a project by name."""
        return self.project_service.get_project(name)

    def _open_fe_url(self, project_name: str) -> None:
        """Open the frontend URL of the project."""
        if project := self._get_project(project_name):
            if project.fe_url:
                logger.debug(f"Opening frontend URL: {project.fe_url}")
                webbrowser.open(project.fe_url)

    def _open_be_url(self, project_name: str) -> None:
        """Open the backend URL of the project."""
        if project := self._get_project(project_name):
            if project.be_url:
                logger.debug(f"Opening backend URL: {project.be_url}")
                webbrowser.open(project.be_url)

    def _open_in_cursor(self, project_name: str) -> None:
        """Open the project in Cursor IDE."""
        if project := self._get_project(project_name):
            logger.debug(f"Opening project in Cursor: {project.directory}")
            try:
                subprocess.run(['cursor', str(project.directory)], check=True)
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to open Cursor IDE")
            except FileNotFoundError:
                messagebox.showerror("Error", "Cursor IDE not found. Is it installed?")

    def _edit_project(self, project_name: str) -> None:
        """Open the edit dialog for the project."""
        if project := self._get_project(project_name):
            from .edit_dialog import EditDialog
            EditDialog(self.frame, project, self.project_service, self.load_projects)

    def _refresh_projects(self) -> None:
        """Refresh projects from filesystem and update UI."""
        logger.debug("Refreshing projects...")
        
        # Force a complete rescan from filesystem
        self.project_service.rescan_projects()
        
        # Reload UI
        self.load_projects()
        
        # Show toast notification
        self.toast.show("Projects refreshed")