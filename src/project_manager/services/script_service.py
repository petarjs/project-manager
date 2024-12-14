from pathlib import Path
import os
import subprocess
import random
import json
from typing import Callable, Optional
import pymysql
from pymysql.err import Error

from ..utils.config import NEW_PROJECT_SCRIPT


class ScriptService:
    """Service for executing shell scripts and capturing their output."""

    def _run_command(
        self, 
        command: str, 
        output_callback: Optional[Callable[[str], None]] = None,
        cwd: Optional[Path] = None,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a command and stream its output.
        
        Args:
            command: Command to run
            output_callback: Callback for output
            cwd: Working directory
            check: Whether to raise on error
            
        Returns:
            CompletedProcess instance
            
        Raises:
            subprocess.CalledProcessError: If command fails and check=True
        """
        if output_callback:
            output_callback(f"$ {command}")
            
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=cwd,
            bufsize=1  # Line buffered
        )
        
        output_lines = []
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                line = line.strip()
                output_lines.append(line)
                if output_callback:
                    output_callback(line)
                    
        process.stdout.close()
        return_code = process.wait()
        
        if check and return_code != 0:
            error_msg = '\n'.join(output_lines)
            if output_callback:
                output_callback(f"\nCommand failed with exit code {return_code}")
                output_callback(f"Error output:\n{error_msg}")
            raise subprocess.CalledProcessError(
                return_code, command, error_msg
            )
            
        return subprocess.CompletedProcess(
            command, return_code, '\n'.join(output_lines)
        )

    def _generate_random_color(self) -> str:
        """Generate a random color hex code."""
        return '%02x%02x%02x' % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    def _update_vscode_settings(
        self, 
        project_dir: Path, 
        color: str,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """Update VS Code settings with project color."""
        if output_callback:
            output_callback(f"Updating VS Code settings with color #{color}...")
            
        settings_dir = project_dir / ".vscode"
        settings_dir.mkdir(exist_ok=True)
        
        settings_file = settings_dir / "settings.json"
        settings = {
            "cSpell.words": ["superadmin"],
            "workbench.colorCustomizations": {
                "statusBar.background": f"#{color}",
                "statusBar.foreground": "#ffffff",
                "titleBar.activeBackground": f"#{color}",
                "titleBar.activeForeground": "#ffffff",
                "titleBar.inactiveBackground": f"#{color}",
                "titleBar.inactiveForeground": "#e7e7e799"
            }
        }
        
        settings_file.write_text(json.dumps(settings, indent=2))

    def _create_database(
        self, 
        db_name: str,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """Create a MySQL database."""
        if output_callback:
            output_callback(f"Creating database {db_name}...")
            
        try:
            connection = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="",
                charset='utf8mb4'
            )
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
            connection.commit()
            if output_callback:
                output_callback(f"Database {db_name} created successfully")
        except Error as e:
            if output_callback:
                output_callback(f"Error creating database: {e}")
            raise
        finally:
            if 'connection' in locals() and connection:
                connection.close()

    def _drop_database(
        self, 
        db_name: str,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """Drop a MySQL database."""
        if output_callback:
            output_callback(f"Dropping database {db_name}...")
            
        try:
            connection = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="",
                charset='utf8mb4'
            )
            with connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
            connection.commit()
            if output_callback:
                output_callback(f"Database {db_name} dropped successfully")
        except Error as e:
            if output_callback:
                output_callback(f"Error dropping database: {e}")
            raise
        finally:
            if 'connection' in locals() and connection:
                connection.close()

    def delete_project(
        self,
        app_name: str,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """Delete a project and all its resources.
        
        Args:
            app_name: Name of the project to delete
            output_callback: Optional callback for output
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if output_callback:
                output_callback(f"Deleting project {app_name}...")
            
            # Drop database
            self._drop_database(app_name, output_callback)
            
            # Delete GitHub repositories
            if output_callback:
                output_callback("\nDeleting GitHub repositories...")
            self._run_command(
                f'gh repo delete --yes petarjs/{app_name}-api',
                output_callback
            )
            self._run_command(
                f'gh repo delete --yes petarjs/{app_name}-app',
                output_callback
            )
            
            # Remove Herd proxies
            if output_callback:
                output_callback("\nRemoving Herd proxies...")
            self._run_command(
                f'herd unproxy app.{app_name}',
                output_callback,
                check=False  # Don't fail if proxy doesn't exist
            )
            self._run_command(
                f'herd unlink api.{app_name}',
                output_callback,
                check=False  # Don't fail if link doesn't exist
            )
            
            # Delete project directory
            if output_callback:
                output_callback("\nDeleting project directory...")
            project_dir = Path.home() / "projects" / "personal" / app_name
            if project_dir.exists():
                import shutil
                shutil.rmtree(project_dir)
                if output_callback:
                    output_callback(f"Deleted directory: {project_dir}")
            
            if output_callback:
                output_callback("\nProject deleted successfully! 🗑️")
            
            return True
            
        except Exception as e:
            if output_callback:
                output_callback(f"\nError deleting project: {str(e)}")
            return False

    def execute_new_project_script(
        self,
        app_name: str,
        app_name_pretty: str,
        port: int,
        redis_db: int,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """Create a new project with the given parameters."""
        try:
            projects_dir = Path.home() / "projects" / "personal"
            project_dir = projects_dir / app_name
            
            # Log project details
            if output_callback:
                output_callback("Creating new project with:")
                output_callback(f"  App Name: {app_name}")
                output_callback(f"  Display Name: {app_name_pretty}")
                output_callback(f"  Port: {port}")
                output_callback(f"  Redis DB: {redis_db}")
                output_callback("")
            
            # Create project directory
            project_dir.mkdir(exist_ok=True)
            
            # Create repositories
            if output_callback:
                output_callback("Creating repositories...")
                
            self._run_command(
                f'gh repo create {app_name}-api --template petarjs/api.saasdev --private --clone',
                output_callback,
                cwd=project_dir
            )
            self._run_command(
                f'gh repo create {app_name}-app --template petarjs/www.saasdev --private --clone',
                output_callback,
                cwd=project_dir
            )
            
            # Frontend setup
            if output_callback:
                output_callback("\nSetting up frontend...")
                
            frontend_dir = project_dir / f"{app_name}-app"
            
            self._run_command('pnpm i', output_callback, cwd=frontend_dir)
            
            # Update package.json
            pkg_file = frontend_dir / "package.json"
            with open(pkg_file) as f:
                pkg_data = json.load(f)
            
            # Update scripts that contain port number
            for script in pkg_data.get('scripts', {}).values():
                if '-p 3000' in script:
                    script.replace('-p 3000', f'-p {port}')
            pkg_data['name'] = app_name
            
            with open(pkg_file, 'w') as f:
                json.dump(pkg_data, f, indent=2)
            
            # Set up frontend proxy
            if output_callback:
                output_callback("Setting up frontend proxy...")
            self._run_command(
                f'herd proxy --secure app.{app_name} http://localhost:{port}',
                output_callback
            )
            
            # Set up frontend .env
            env_example = frontend_dir / ".env.example"
            env_local = frontend_dir / ".env.local"
            
            if env_example.exists():
                env_content = env_example.read_text()
                env_content = env_content.replace('https://api.saasdev.test', f'https://api.{app_name}.test')
                env_content = env_content.replace('https://saasdev.test', f'https://app.{app_name}.test')
                env_content = env_content.replace('SaasDev', app_name_pretty)
                env_local.write_text(env_content)
            
            # Backend setup
            if output_callback:
                output_callback("\nSetting up backend...")
                
            backend_dir = project_dir / f"{app_name}-api"
            
            # Create database
            self._create_database(app_name, output_callback)
            
            # Set up backend proxy
            if output_callback:
                output_callback("Setting up backend proxy...")
            self._run_command(
                f'herd link --secure api.{app_name}.test',
                output_callback
            )
            
            # Set up backend .env
            env_example = backend_dir / ".env.example"
            env_file = backend_dir / ".env"
            
            if env_example.exists():
                env_content = env_example.read_text()
                replacements = {
                    'DB_DATABASE=.*': f'DB_DATABASE={app_name}',
                    'APP_NAME=.*': f'APP_NAME="{app_name_pretty}"',
                    'APP_URL=.*': f'APP_URL=https://api.{app_name}.test',
                    'FRONTEND_URL=.*': f'FRONTEND_URL=https://app.{app_name}.test',
                    'CORS_ALLOWED_ORIGIN=.*': f'CORS_ALLOWED_ORIGIN=https://app.{app_name}.test',
                    'SANCTUM_STATEFUL_DOMAINS=.*': f'SANCTUM_STATEFUL_DOMAINS=https://app.{app_name}.test',
                    'SESSION_DOMAIN=.*': f'SESSION_DOMAIN=.{app_name}.test',
                    'REDIS_CACHE_DB=.*': f'REDIS_CACHE_DB={redis_db}',
                    'REDIS_DB=.*': f'REDIS_DB={redis_db}'
                }
                
                for pattern, replacement in replacements.items():
                    import re
                    env_content = re.sub(pattern, replacement, env_content)
                    
                env_file.write_text(env_content)
            
            # Install backend dependencies
            if output_callback:
                output_callback("Installing backend dependencies...")
            self._run_command('composer install', output_callback, cwd=backend_dir)
            
            # Set up Laravel
            if output_callback:
                output_callback("Setting up Laravel...")
            self._run_command('php artisan key:generate', output_callback, cwd=backend_dir)
            self._run_command('php artisan migrate:fresh --seed', output_callback, cwd=backend_dir)
            self._run_command('php artisan storage:link', output_callback, cwd=backend_dir)
            
            # Set up IP Info
            (backend_dir / "storage/app/ipinfo").mkdir(parents=True, exist_ok=True)
            self._run_command('php artisan ipinfo:update', output_callback, cwd=backend_dir)
            
            # Update VS Code settings for both directories
            color = self._generate_random_color()
            self._update_vscode_settings(frontend_dir, color, output_callback)
            self._update_vscode_settings(backend_dir, color, output_callback)
            
            # Final output
            if output_callback:
                output_callback("\nProject setup complete! 🎉")
                output_callback("")
                output_callback(f"Frontend URL: https://app.{app_name}.test")
                output_callback(f"Backend URL: https://api.{app_name}.test")
                output_callback("")
                output_callback(f"Frontend directory: {frontend_dir}")
                output_callback(f"Backend directory: {backend_dir}")
                output_callback("")
                output_callback(f"Port: {port}")
                output_callback(f"Redis DB: {redis_db}")
                output_callback(f"Database: {app_name}")
            
            return True
            
        except Exception as e:
            if output_callback:
                output_callback(f"\nError: {str(e)}")
            return False 