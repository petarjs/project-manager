from pathlib import Path
from typing import Final

# Project paths
HOME: Final[Path] = Path.home()
PROJECTS_DIR: Final[Path] = HOME / "projects" / "personal"
SCRIPTS_DIR: Final[Path] = HOME / "projects" / "scripts"
PROJECT_DATA_FILE: Final[Path] = PROJECTS_DIR / ".projects.json"

# Script paths
NEW_PROJECT_SCRIPT: Final[Path] = SCRIPTS_DIR / "start-new-project.sh"

# Port configuration
MIN_PORT: Final[int] = 3000
MAX_PORT: Final[int] = 3999

# Redis configuration
MIN_REDIS_DB: Final[int] = 0
MAX_REDIS_DB: Final[int] = 999