"""
Window Centering Utility for Super Scholars
Cross-platform centering for Windows and Linux
"""

import tkinter as tk
import sys


def center_window(window, width=None, height=None):
    """
    Center a window on the screen - works on Windows and Linux
    
    Args:
        window: The tkinter/customtkinter window to center
        width: Optional width to use (if not set, uses window's current width)
        height: Optional height to use (if not set, uses window's current height)
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
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    x = max(0, min(x, screen_width - width))
    y = max(0, min(y, screen_height - height))
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def maximize_window_full(window):
    """
    Maximize a window to fill the ENTIRE screen - works on Windows and Linux
    
    Args:
        window: The tkinter/customtkinter window to maximize
    """
    window.update_idletasks()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    window.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # On Windows, use the zoomed state for true maximization
    if sys.platform.startswith('win'):
        try:
            window.state('zoomed')
        except:
            pass


def center_and_maximize(window, width=None, height=None):
    """
    Center and maximize a window - fills 95% of the screen
    
    Args:
        window: The tkinter/customtkinter window
        width: Optional width (if None, uses 95% of screen width)
        height: Optional height (if None, uses 95% of screen height)
    """
    window.update_idletasks()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    if width is None:
        width = int(screen_width * 0.95)
    if height is None:
        height = int(screen_height * 0.95)
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    x = max(0, min(x, screen_width - width))
    y = max(0, min(y, screen_height - height))
    
    window.geometry(f"{width}x{height}+{x}+{y}")