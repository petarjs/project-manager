from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Project:
    """
    Represents a local development project with its configuration.

    Attributes:
        name: The project's name (used in directory structure)
        pretty_name: A human-readable name for the project
        port: The port number assigned to this project
        redis_db: The Redis database number assigned to this project
        directory: Path to the project's root directory
        fe_url: Frontend URL for the project
        be_url: Backend URL for the project
        fe_process_pid: The PID of the frontend process
    """

    name: str
    pretty_name: str
    port: int
    redis_db: Optional[int]
    directory: Path
    fe_url: Optional[str] = None
    be_url: Optional[str] = None
    fe_process_pid: Optional[int] = None

    def __post_init__(self) -> None:
        """Set default URLs if not provided."""
        if not self.fe_url:
            self.fe_url = f"https://app.{self.name}.test"
        if not self.be_url:
            self.be_url = f"https://api.{self.name}.test" 