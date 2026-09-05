"""
Window Centering Utility for Super Scholars
Cross-platform centering for Windows and Linux
"""

import tkinter as tk


def center_window(window, width=None, height=None):
    """
    Center a window on the screen - works on Windows and Linux
    """
    # Force update to get actual window dimensions
    window.update_idletasks()
    
    # Get window dimensions
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
    
    # If dimensions are still 1x1 (not yet rendered), use requested size
    if width <= 1 or height <= 1:
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate centered position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Ensure window is fully visible (not off-screen)
    x = max(0, min(x, screen_width - width))
    y = max(0, min(y, screen_height - height))
    
    # Set geometry with position
    window.geometry(f"{width}x{height}+{x}+{y}")


def center_window_position_only(window):
    """
    Center a window while preserving its current size
    Use this for resizable windows/dashboards
    """
    window.update_idletasks()
    
    width = window.winfo_width()
    height = window.winfo_height()
    
    # If not yet sized, use the geometry string if present
    geometry = window.geometry()
    if geometry and "x" in geometry:
        try:
            size_part = geometry.split("+")[0]
            if "x" in size_part:
                w_str, h_str = size_part.split("x")
                if w_str.isdigit() and h_str.isdigit():
                    width = int(w_str)
                    height = int(h_str)
        except:
            pass
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate centered position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Ensure window is fully visible
    x = max(0, min(x, screen_width - width))
    y = max(0, min(y, screen_height - height))
    
    # Set position only (preserve size)
    window.geometry(f"+{x}+{y}")


def maximize_window(window):
    """
    Maximize a window to fill the screen - works on both Windows and Linux
    """
    window.update_idletasks()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Set window to fill the screen (maximized)
    window.geometry(f"{screen_width}x{screen_height}+0+0")


def center_and_maximize(window, width=None, height=None):
    """
    Center and maximize a window - keeps it centered but fills most of the screen
    """
    window.update_idletasks()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Use provided dimensions or 90% of screen
    if width is None:
        width = int(screen_width * 0.90)
    if height is None:
        height = int(screen_height * 0.90)
    
    # Calculate centered position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Ensure window is fully visible
    x = max(0, min(x, screen_width - width))
    y = max(0, min(y, screen_height - height))
    
    # Set geometry with position
    window.geometry(f"{width}x{height}+{x}+{y}")