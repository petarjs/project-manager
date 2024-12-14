import tkinter as tk
from typing import Optional
import time
import threading


class Toast:
    """A toast notification component that shows a temporary message."""
    
    def __init__(self, parent: tk.Widget) -> None:
        """Initialize the toast notification.
        
        Args:
            parent: The parent widget to attach the toast to
        """
        self.parent = parent
        self.window: Optional[tk.Toplevel] = None
        
    def show(self, message: str, duration: float = 2.0) -> None:
        """Show a toast notification with the given message.
        
        Args:
            message: The message to display
            duration: How long to show the message in seconds
        """
        # If there's an existing toast, destroy it
        if self.window is not None:
            self.window.destroy()
            
        # Create new window
        self.window = tk.Toplevel(self.parent)
        self.window.overrideredirect(True)  # Remove window decorations
        
        # Create label with message
        label = tk.Label(
            self.window,
            text=message,
            padx=20,
            pady=10,
            bg='#333333',
            fg='white',
            font=('Arial', 10)
        )
        label.pack()
        
        # Position the window at the bottom right of the parent
        self.window.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        toast_x = parent_x + parent_width - self.window.winfo_width() - 20
        toast_y = parent_y + parent_height - self.window.winfo_height() - 20
        
        self.window.geometry(f"+{toast_x}+{toast_y}")
        
        # Start a thread to close the toast after duration
        def close_toast() -> None:
            time.sleep(duration)
            if self.window is not None:
                self.window.destroy()
                self.window = None
                
        threading.Thread(target=close_toast, daemon=True).start() 