"""
Window Manager - Cross-platform window sizing and centering
Measures screen resolution and sizes windows to fit perfectly (100% full screen)
Works on both Windows and Linux
"""

import tkinter as tk
import sys


def get_screen_dimensions(window):
    """
    Get the actual usable screen dimensions.
    Returns (screen_width, screen_height)
    """
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    return screen_width, screen_height


def fit_window_fullscreen(window):
    """
    Size window to 100% of screen and position at top-left (0,0).
    This fills the entire screen without using OS maximize/minimize.
    
    Works on both Windows and Linux - uses pure geometry() calls.
    """
    window.update_idletasks()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Set geometry to fill entire screen at top-left
    window.geometry(f"{screen_width}x{screen_height}+0+0")
    
    window.update_idletasks()


def apply_fullscreen(window):
    """
    Apply fullscreen sizing with multiple safety delays.
    Call this AFTER the window has been created.
    
    Fires 3 times to ensure it sticks on both Windows and Linux.
    """
    window.after(10, lambda: fit_window_fullscreen(window))
    window.after(100, lambda: fit_window_fullscreen(window))
    window.after(300, lambda: fit_window_fullscreen(window))


def center_window_to_screen(window, width=None, height=None):
    """
    Center a window at a specific size (or its current size).
    Used for dialogs and smaller windows.
    """
    window.update_idletasks()
    
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
    
    if width <= 1 or height <= 1:
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    max_width = int(screen_width * 0.95)
    max_height = int(screen_height * 0.95)
    
    if width > max_width:
        width = max_width
    if height > max_height:
        height = max_height
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    x = max(0, min(x, screen_width - width))
    y = max(0, min(y, screen_height - height))
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def center_dialog(window, width, height):
    """
    Center a dialog window (Toplevel) with fixed size.
    """
    window.update_idletasks()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    max_width = int(screen_width * 0.95)
    max_height = int(screen_height * 0.95)
    
    if width > max_width:
        width = max_width
    if height > max_height:
        height = max_height
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    x = max(0, min(x, screen_width - width))
    y = max(0, min(y, screen_height - height))
    
    window.geometry(f"{width}x{height}+{x}+{y}")