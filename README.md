# Project Manager

A lightweight desktop app for macOS that simplifies local project management. Easily create new projects using boilerplate scripts, view and manage existing projects, and launch frontend/backend URLs or open projects in Cursor IDE.

## Features

- View and manage local development projects
- Create new projects from boilerplate
- Open project URLs and IDE directly
- macOS status bar integration
- Automatic port and Redis DB assignment

## Development

### Setup

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   # Install uv for faster package management
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv pip install -e ".[dev]"
   ```

3. Run the app:
   ```bash
   python -m project_manager
   ```

The app will appear in your macOS status bar with a rocket icon (🚀). Click it to:

- View and manage your projects
- Open project URLs
- Launch Cursor IDE
- Create new projects

## Requirements

- Python 3.9 or higher
- macOS (for status bar integration)
- Cursor IDE installed
- GitHub CLI (gh) installed
