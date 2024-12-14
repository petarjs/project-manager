import logging
import webbrowser
import subprocess
from pathlib import Path
from typing import Optional
import rumps
import sys
import os

from ..services.project_service import ProjectService
from ..services.script_service import ScriptService

logger = logging.getLogger(__name__)

# Get the path to the assets directory
ASSETS_DIR = Path(__file__).parent.parent / "assets"
ICON_PATH = ASSETS_DIR / "icon.png"

class ProjectManagerStatusBar(rumps.App):
    """Status bar app for Project Manager."""

    def __init__(
        self,
        project_service: ProjectService,
        script_service: ScriptService
    ) -> None:
        """Initialize the status bar app.
        
        Args:
            project_service: Project service instance
            script_service: Script service instance
        """
        # Make sure assets directory exists
        ASSETS_DIR.mkdir(exist_ok=True)
        
        # Create a simple icon if it doesn't exist
        if not ICON_PATH.exists():
            self._create_default_icon()
        
        # Initialize with icon
        super().__init__(
            "PM",
            icon=str(ICON_PATH),
            quit_button="Quit",
        )
        
        self.project_service = project_service
        self.script_service = script_service
        
        # Set up initial menu
        self.menu = [
            rumps.MenuItem("Projects:"),  # Header for projects section
            rumps.MenuItem("No projects found"),  # Default item
            None,  # Separator
            rumps.MenuItem("Refresh", callback=self.refresh_projects),
            None,  # Separator
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        # Load initial projects after a delay
        rumps.Timer(self.on_ready, 1).start()
    
    def _create_default_icon(self) -> None:
        """Create a simple default icon."""
        try:
            # Create a simple 32x32 PNG with a gear icon
            from PIL import Image, ImageDraw
            
            # Create a new image with a transparent background
            img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a simple gear icon
            # Outer circle
            draw.ellipse([4, 4, 28, 28], outline=(0, 0, 0, 255), width=2)
            # Inner circle
            draw.ellipse([12, 12, 20, 20], fill=(0, 0, 0, 255))
            
            # Save the icon
            img.save(ICON_PATH)
            logger.debug(f"Created default icon at {ICON_PATH}")
        except Exception as e:
            logger.error(f"Failed to create default icon: {e}")
            # If we can't create the icon, we'll fall back to text
    
    def on_ready(self, _: rumps.Timer) -> None:
        """Handle app ready event."""
        self.refresh_projects()
    
    def refresh_projects(self, _: Optional[rumps.MenuItem] = None) -> None:
        """Refresh the projects list in the menu."""
        logger.debug("Refreshing status bar projects menu")
        
        # Force project rescan
        self.project_service.rescan_projects()
        
        # Build menu from scratch
        new_menu = [
            rumps.MenuItem("Projects:"),  # Header
        ]
        
        # Add projects
        if self.project_service.projects:
            for project in self.project_service.projects:
                project_menu = rumps.MenuItem(project.pretty_name)
                project_menu.update([
                    rumps.MenuItem(
                        "Open Frontend",
                        callback=lambda x, url=project.fe_url: webbrowser.open(url) if url else None
                    ),
                    rumps.MenuItem(
                        "Open Backend",
                        callback=lambda x, url=project.be_url: webbrowser.open(url) if url else None
                    ),
                    rumps.MenuItem(
                        "Open in Cursor",
                        callback=lambda x, dir=project.directory: subprocess.run(['cursor', str(dir)], check=True)
                    )
                ])
                new_menu.append(project_menu)
        else:
            no_projects = rumps.MenuItem("No projects found")
            no_projects.set_callback(None)  # Make it non-clickable
            new_menu.append(no_projects)
        
        # Add remaining menu items
        new_menu.extend([
            None,  # Separator
            rumps.MenuItem("Refresh", callback=self.refresh_projects),
            None,  # Separator
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ])
        
        # Replace entire menu
        self.menu.clear()
        self.menu = new_menu