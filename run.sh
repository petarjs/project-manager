#!/bin/bash
export TK_SILENCE_DEPRECATION=1

echo "Python version:"
python3.12 --version

echo "Tkinter version:"
python3.12 -c "import tkinter; print(f'Tkinter version: {tkinter.TkVersion}')"

echo "Starting application..."
PYTHONPATH=src python3.12 -m project_manager 