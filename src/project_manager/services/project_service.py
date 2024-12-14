import json
import logging
from pathlib import Path
from typing import List, Optional, Dict

from ..models.project import Project
from ..utils.config import PROJECT_DATA_FILE, PROJECTS_DIR, MIN_PORT, MAX_PORT, MIN_REDIS_DB, MAX_REDIS_DB

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for managing local development projects."""

    def __init__(self) -> None:
        """Initialize the ProjectService."""
        self.projects: List[Project] = []
        self._load_projects()

    def _extract_port_from_script(self, script: str) -> Optional[int]:
        """
        Extract port number from a script command.
        
        Args:
            script: Script command string
            
        Returns:
            Port number if found, None otherwise
        """
        # Common patterns for port specification
        patterns = [
            r'next\s+dev\s+-p\s*(\d+)',  # next dev -p 3000
            r'next\s+dev.*?-p\s*(\d+)',  # next dev with stuff before -p
            r'-p\s*(\d+)',               # -p 3000 or -p3000
            r'--port\s*(\d+)',           # --port 3000 or --port=3000
            r'PORT=(\d+)',               # PORT=3000
        ]
        
        logger.debug(f"Checking script for port: {script}")
        for pattern in patterns:
            import re
            if match := re.search(pattern, script, re.IGNORECASE):  # Make search case-insensitive
                try:
                    port = int(match.group(1))
                    logger.debug(f"Found port {port} using pattern {pattern}")
                    return port
                except ValueError:
                    continue
        return None

    def _read_package_json(self, project_dir: Path) -> Dict:
        """
        Read package.json from project directory.
        
        Args:
            project_dir: Project directory path
            
        Returns:
            Dict containing package.json data or empty dict if not found
        """
        # First check frontend locations
        fe_locations = [
            project_dir / "www" / "package.json",
            project_dir / "app" / "package.json",  # Add plain app directory
            project_dir / f"{project_dir.name}-app" / "package.json",
            project_dir / "package.json"  # fallback
        ]
        
        # Then check backend locations
        be_locations = [
            project_dir / "api" / "package.json",
            project_dir / f"{project_dir.name}-api" / "package.json"
        ]
        
        # Try frontend first, then backend
        for pkg_file in [*fe_locations, *be_locations]:
            logger.debug(f"Checking for package.json at: {pkg_file}")
            if pkg_file.exists():
                try:
                    with open(pkg_file) as f:
                        data = json.load(f)
                        logger.debug(f"Found package.json at {pkg_file}")
                        if 'scripts' in data:
                            logger.debug(f"Scripts found: {data['scripts']}")
                        return data
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in {pkg_file}")
                except Exception as e:
                    logger.warning(f"Error reading {pkg_file}: {e}")
        
        logger.debug("No package.json found")
        return {}

    def _get_port_from_package(self, pkg_data: Dict) -> Optional[int]:
        """
        Extract port number from package.json data.
        
        Args:
            pkg_data: Package.json contents as dict
            
        Returns:
            Port number if found, None otherwise
        """
        if not pkg_data:
            logger.debug("No package.json data provided")
            return None
            
        # Check scripts section
        scripts = pkg_data.get('scripts', {})
        logger.debug(f"Checking scripts: {scripts}")
        
        # First check dev script as it's most likely to have the correct port
        if dev_script := scripts.get('dev'):
            logger.debug(f"Checking dev script: {dev_script}")
            if port := self._extract_port_from_script(dev_script):
                logger.debug(f"Found port {port} in dev script")
                return port
        
        # Then check other common scripts
        for script_name in ['start', 'serve']:
            if script := scripts.get(script_name):
                logger.debug(f"Checking {script_name} script: {script}")
                if port := self._extract_port_from_script(script):
                    logger.debug(f"Found port {port} in {script_name} script")
                    return port
                else:
                    logger.debug(f"No port found in {script_name} script")
        
        # Check next.js config
        if 'next' in pkg_data.get('dependencies', {}):
            next_config = pkg_data.get('config', {})
            logger.debug(f"Checking Next.js config: {next_config}")
            if port := next_config.get('port'):
                try:
                    return int(port)
                except ValueError:
                    pass
        
        logger.debug("No port found in package.json")
        return None

    def _is_valid_port(self, port: int) -> bool:
        """Check if a port number is valid."""
        try:
            port_num = int(port)
            # Any port between 1 and 65535 is technically valid
            is_valid = 1 <= port_num <= 65535
            logger.debug(f"Port {port} validity check: {is_valid}")
            return is_valid
        except (TypeError, ValueError):
            logger.debug(f"Invalid port value: {port}")
            return False

    def _get_next_port(self) -> int:
        """Get next available port number."""
        used_ports = {p.port for p in self.projects}
        logger.debug(f"Finding next port. Currently used: {used_ports}")
        
        if not used_ports:
            default_port = 3000
            logger.debug(f"No ports in use, using default: {default_port}")
            return default_port
        
        # Start with common development ports
        common_ports = [3000, 3001, 3002, 3003, 3004, 3005]
        for port in common_ports:
            if port not in used_ports:
                logger.debug(f"Found available common port: {port}")
                return port
        
        # If no common ports available, use the next port after the highest
        next_port = max(used_ports) + 1
        logger.debug(f"Using next sequential port: {next_port}")
        return next_port

    def _is_laravel_project(self, be_dir: Path) -> bool:
        """Check if this is a Laravel project."""
        composer_json = be_dir / "composer.json"
        if composer_json.exists():
            try:
                with open(composer_json) as f:
                    data = json.load(f)
                    return "laravel/framework" in data.get("require", {})
            except Exception:
                pass
        return False

    def _get_redis_db_from_env(self, project_dir: Path) -> Optional[int]:
        """
        Get Redis DB number from .env file.
        
        Args:
            project_dir: Project directory path
            
        Returns:
            Redis DB number if found, None if not found or invalid
        """
        # Check possible backend locations
        be_locations = [
            project_dir / "api",
            project_dir / f"{project_dir.name}-api"
        ]
        
        logger.debug(f"Checking Redis DB in backend locations for {project_dir.name}")
        
        for be_dir in be_locations:
            env_file = be_dir / ".env"
            logger.debug(f"Checking for .env at: {env_file}")
            
            if env_file.exists():
                logger.debug(f"Found .env file at {env_file}")
                try:
                    with open(env_file) as f:
                        env_content = f.read()
                        logger.debug(f"ENV file contents for {project_dir.name}:\n{env_content}")
                        
                        for line in env_content.splitlines():
                            line = line.strip()
                            if line.startswith(('REDIS_DB=', 'REDIS_CACHE_DB=')):
                                try:
                                    value = line.split('=')[1].strip()
                                    if value:  # Only parse if value is not empty
                                        redis_db = int(value)
                                        logger.debug(f"Found Redis DB value: {redis_db}")
                                        return redis_db
                                except (IndexError, ValueError) as e:
                                    logger.debug(f"Failed to parse Redis DB value: {e}")
                                    continue
                except Exception as e:
                    logger.warning(f"Error reading .env file: {e}")
            else:
                logger.debug(f"No .env file found at {env_file}")
        
        logger.debug(f"No Redis DB found for {project_dir.name}")
        return None

    def _scan_projects_directory(self) -> None:
        """Scan the projects directory for untracked projects."""
        logger.debug(f"Scanning directory: {PROJECTS_DIR}")
        
        # Track used ports to avoid duplicates
        used_ports = {p.port for p in self.projects}
        logger.debug(f"Currently used ports: {used_ports}")
        
        # Initialize project data dictionary
        project_data = {}
        
        for path in PROJECTS_DIR.iterdir():
            if not path.is_dir():
                continue
            
            if not any(p.name == path.name for p in self.projects):
                name = path.name
                logger.debug(f"\nProcessing project directory: {name}")
                
                # Try to detect project structure
                app_dir = path / f"{name}-app"
                api_dir = path / f"{name}-api"
                www_dir = path / "www"
                standard_api_dir = path / "api"
                plain_app_dir = path / "app"
                
                # Check all three possible structures
                has_named_app_api = app_dir.exists() and api_dir.exists()
                has_plain_app_api = plain_app_dir.exists() and standard_api_dir.exists()
                has_www_api = www_dir.exists() and standard_api_dir.exists()
                
                if has_named_app_api or has_plain_app_api or has_www_api:
                    # Read package.json for port number
                    pkg_data = self._read_package_json(path)
                    detected_port = self._get_port_from_package(pkg_data)
                    
                    # Get Redis DB from .env
                    redis_db = self._get_redis_db_from_env(path)
                    logger.debug(f"Detected Redis DB for {name}: {redis_db}")
                    
                    # If no port detected, assign a new one
                    if not detected_port or not self._is_valid_port(detected_port):
                        detected_port = self._get_next_port()
                        logger.debug(f"Assigned new port {detected_port} for {name}")
                    
                    logger.debug(f"Found new project {name} with port {detected_port}")
                    project_data[name] = {
                        "name": name,
                        "pretty_name": name.replace('-', ' ').title(),
                        "port": detected_port,
                        "redis_db": redis_db,
                        "directory": path,
                        "fe_url": f"https://app.{name}.test",
                        "be_url": f"https://api.{name}.test"
                    }
        
        # Add new projects to self.projects
        for data in project_data.values():
            project = Project(**data)
            self.projects.append(project)
            logger.debug(f"Added new project: {project.name}")
        
        # Save if we found any new projects
        if project_data:
            self.save_projects()
            logger.debug(f"Saved {len(project_data)} new projects")

    def _load_projects(self) -> None:
        """Load projects from the data file and scan the projects directory."""
        logger.debug("Loading projects...")
        
        # Track all project directories and their data
        project_data = {}
        
        # First load saved data
        if PROJECT_DATA_FILE.exists():
            logger.debug(f"Loading saved data from {PROJECT_DATA_FILE}")
            try:
                with open(PROJECT_DATA_FILE, "r") as f:
                    saved_data = json.load(f)
                    for data in saved_data:
                        name = data["name"]
                        # Convert directory string to Path
                        directory = Path(data['directory'])
                        
                        # Skip if directory doesn't exist
                        if not directory.exists():
                            logger.debug(f"Skipping {name} - directory not found: {directory}")
                            continue
                            
                        # Skip if neither frontend nor backend exists
                        app_dir = directory / f"{name}-app"
                        api_dir = directory / f"{name}-api"
                        www_dir = directory / "www"
                        standard_api_dir = directory / "api"
                        plain_app_dir = directory / "app"
                        
                        # Check all three possible structures
                        has_named_app_api = app_dir.exists() and api_dir.exists()
                        has_plain_app_api = plain_app_dir.exists() and standard_api_dir.exists()
                        has_www_api = www_dir.exists() and standard_api_dir.exists()
                        
                        if not (has_named_app_api or has_plain_app_api or has_www_api):
                            logger.debug(f"Skipping {name} - no valid project structure found")
                            continue
                        
                        data['directory'] = directory
                        
                        # Check for Redis DB in .env even for saved projects
                        redis_db = self._get_redis_db_from_env(directory)
                        if redis_db is not None:
                            data['redis_db'] = redis_db
                            logger.debug(f"Updated Redis DB for {name} to {redis_db}")
                        
                        # Re-check port from package.json
                        pkg_data = self._read_package_json(directory)
                        if detected_port := self._get_port_from_package(pkg_data):
                            if detected_port != data.get('port'):
                                logger.debug(f"Updating port for {name} from {data.get('port')} to {detected_port}")
                                data['port'] = detected_port
                        
                        project_data[name] = data
                        logger.debug(f"Loaded saved project: {name} (port={data['port']}, redis_db={data['redis_db']})")
            except Exception as e:
                logger.error(f"Error loading projects file: {e}")
        
        # Then scan directory for new projects only
        for path in PROJECTS_DIR.iterdir():
            if not path.is_dir():
                continue
                
            name = path.name
            if name not in project_data:  # Only process new projects
                # Try to detect project structure
                app_dir = path / f"{name}-app"
                api_dir = path / f"{name}-api"
                www_dir = path / "www"
                standard_api_dir = path / "api"
                plain_app_dir = path / "app"
                
                # Check all three possible structures
                has_named_app_api = app_dir.exists() and api_dir.exists()
                has_plain_app_api = plain_app_dir.exists() and standard_api_dir.exists()
                has_www_api = www_dir.exists() and standard_api_dir.exists()
                
                if has_named_app_api or has_plain_app_api or has_www_api:
                    # Read package.json for port number
                    pkg_data = self._read_package_json(path)
                    detected_port = self._get_port_from_package(pkg_data)
                    
                    # Get Redis DB from .env
                    redis_db = self._get_redis_db_from_env(path)
                    logger.debug(f"Detected Redis DB for {name}: {redis_db}")
                    
                    # If no port detected, assign a new one
                    if not detected_port or not self._is_valid_port(detected_port):
                        detected_port = self._get_next_port()
                        logger.debug(f"Assigned new port {detected_port} for {name}")
                    
                    logger.debug(f"Found new project {name} with port {detected_port}")
                    project_data[name] = {
                        "name": name,
                        "pretty_name": name.replace('-', ' ').title(),
                        "port": detected_port,
                        "redis_db": redis_db,
                        "directory": path,
                        "fe_url": f"https://app.{name}.test",
                        "be_url": f"https://api.{name}.test"
                    }
        
        # Create Project objects
        self.projects = []
        for data in project_data.values():
            self.projects.append(Project(**data))
            logger.debug(f"Added project {data['name']} with port={data['port']}, redis_db={data['redis_db']}")
        
        # Save to update the projects file with only existing projects
        self.save_projects()
        
        logger.debug(f"Total projects loaded: {len(self.projects)}")

    def save_projects(self) -> None:
        """Save project data to the data file."""
        logger.debug(f"Saving {len(self.projects)} projects to {PROJECT_DATA_FILE}")
        
        # Create parent directory if it doesn't exist
        PROJECT_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = [
            {
                "name": p.name,
                "pretty_name": p.pretty_name,
                "port": p.port,
                "redis_db": p.redis_db,
                "directory": str(p.directory),
                "fe_url": p.fe_url,
                "be_url": p.be_url
            }
            for p in self.projects
        ]
        
        try:
            # Log the data being saved
            logger.debug(f"Project data to save: {json.dumps(data, indent=2)}")
            
            # Write to a temporary file first
            temp_file = PROJECT_DATA_FILE.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Rename temp file to actual file (atomic operation)
            temp_file.replace(PROJECT_DATA_FILE)
            
            logger.debug("Successfully saved projects file")
            
            # Verify the save
            if PROJECT_DATA_FILE.exists():
                with open(PROJECT_DATA_FILE) as f:
                    saved_data = json.load(f)
                    logger.debug(f"Verified saved data contains {len(saved_data)} projects")
            
        except Exception as e:
            logger.error(f"Error saving projects file: {e}", exc_info=True)
            raise

    def get_project(self, name: str) -> Optional[Project]:
        """
        Get a project by name.

        Args:
            name: The project name to look up

        Returns:
            The Project if found, None otherwise
        """
        return next((p for p in self.projects if p.name == name), None)

    def add_project(self, project: Project) -> None:
        """
        Add a new project.

        Args:
            project: The Project to add
        """
        self.projects.append(project)
        self.save_projects() 

    def update_project(self, name: str, updates: dict) -> Optional[Project]:
        """
        Update a project's details.
        
        Args:
            name: Name of the project to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated Project if found, None otherwise
        """
        project = self.get_project(name)
        if not project:
            logger.warning(f"Project not found: {name}")
            return None
            
        logger.debug(f"Updating project {name} with: {updates}")
        
        # Validate port if being updated
        if 'port' in updates:
            new_port = updates['port']
            # Check if port is already in use by another project
            if any(p.port == new_port and p.name != name for p in self.projects):
                logger.warning(f"Port {new_port} is already in use")
                raise ValueError(f"Port {new_port} is already in use")
        
        # Update project attributes
        for key, value in updates.items():
            if hasattr(project, key):
                old_value = getattr(project, key)
                setattr(project, key, value)
                logger.debug(f"Updated {key}: {old_value} -> {value}")
        
        # Save changes immediately
        try:
            self.save_projects()
            logger.debug(f"Successfully updated and saved project {name}")
        except Exception as e:
            logger.error(f"Failed to save project updates: {e}")
            raise
        
        return project

    def _get_next_redis_db(self) -> int:
        """Get next available Redis DB number.
        
        Returns:
            int: Next available Redis DB number
        
        Raises:
            ValueError: If no Redis DBs are available
        """
        used_dbs = {p.redis_db for p in self.projects if p.redis_db is not None}
        logger.debug(f"Finding next Redis DB. Currently used: {used_dbs}")
        
        if not used_dbs:
            default_db = MIN_REDIS_DB
            logger.debug(f"No Redis DBs in use, using default: {default_db}")
            return default_db
            
        # Try to find the first available DB in sequence
        current_db = MIN_REDIS_DB
        while current_db <= MAX_REDIS_DB:
            if current_db not in used_dbs:
                logger.debug(f"Found available Redis DB: {current_db}")
                return current_db
            current_db += 1
            
        raise ValueError(f"No Redis DBs available in range {MIN_REDIS_DB}-{MAX_REDIS_DB}")

    def rescan_projects(self) -> None:
        """Force a complete rescan of projects from filesystem, ignoring cached data."""
        logger.debug("Forcing complete project rescan from filesystem...")
        
        # Track all project directories and their data
        project_data = {}
        
        # Scan all directories
        for path in PROJECTS_DIR.iterdir():
            if not path.is_dir():
                continue
                
            name = path.name
            logger.debug(f"\nProcessing project directory: {name}")
            
            # Try to detect project structure
            app_dir = path / f"{name}-app"
            api_dir = path / f"{name}-api"
            www_dir = path / "www"
            standard_api_dir = path / "api"
            plain_app_dir = path / "app"
            
            # Check all three possible structures
            has_named_app_api = app_dir.exists() and api_dir.exists()
            has_plain_app_api = plain_app_dir.exists() and standard_api_dir.exists()
            has_www_api = www_dir.exists() and standard_api_dir.exists()
            
            if has_named_app_api or has_plain_app_api or has_www_api:
                # Read package.json for port number
                pkg_data = self._read_package_json(path)
                detected_port = self._get_port_from_package(pkg_data)
                
                # Get Redis DB from .env
                redis_db = self._get_redis_db_from_env(path)
                logger.debug(f"Detected Redis DB for {name}: {redis_db}")
                
                # If no port detected, assign a new one
                if not detected_port or not self._is_valid_port(detected_port):
                    detected_port = self._get_next_port()
                    logger.debug(f"Assigned new port {detected_port} for {name}")
                
                logger.debug(f"Found project {name} with port {detected_port}")
                project_data[name] = {
                    "name": name,
                    "pretty_name": name.replace('-', ' ').title(),
                    "port": detected_port,
                    "redis_db": redis_db,
                    "directory": path,
                    "fe_url": f"https://app.{name}.test",
                    "be_url": f"https://api.{name}.test"
                }
        
        # Create Project objects
        self.projects = []
        for data in project_data.values():
            self.projects.append(Project(**data))
            logger.debug(f"Added project {data['name']} with port={data['port']}, redis_db={data['redis_db']}")
        
        # Save to update the projects file
        self.save_projects()
        logger.debug(f"Rescan complete. Found {len(self.projects)} projects")