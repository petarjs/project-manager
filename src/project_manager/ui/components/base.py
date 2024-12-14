import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class BaseComponent:
    """Base class for UI components."""
    
    def __init__(self, parent: tk.Widget) -> None:
        """
        Initialize the component.
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.frame = ttk.Frame(parent) 