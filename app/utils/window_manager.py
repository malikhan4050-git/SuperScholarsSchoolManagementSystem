"""
Window Manager - Handles full-screen maximization and centering
Works on both Windows and Linux
"""

import tkinter as tk
import sys


def maximize_window(window):
    """
    Maximize a window to fill the ENTIRE screen (100% full screen)
    Works on both Windows and Linux
    
    Args:
        window: The tkinter/customtkinter window to maximize
    """
    window.update_idletasks()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # On Windows, use the zoomed state for true maximization
    if sys.platform.startswith('win'):
        try:
            window.state('zoomed')
            return
        except:
            pass
    
    # Fallback: Set geometry to full screen (works on Linux)
    window.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # On Linux, we might need to wait for the window to be ready
    window.after(50, lambda: window.geometry(f"{screen_width}x{screen_height}+0+0"))
    window.after(200, lambda: window.geometry(f"{screen_width}x{screen_height}+0+0"))
    window.after(500, lambda: window.geometry(f"{screen_width}x{screen_height}+0+0"))


def center_window(window, width=None, height=None):
    """
    Center a window on the screen (works on Windows and Linux)
    
    Args:
        window: The tkinter/customtkinter window to center
        width: Optional width (if not set, uses current window width)
        height: Optional height (if not set, uses current window height)
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


def maximize_and_center(window):
    """
    Maximize a window to 100% full screen AND ensure it's centered
    This is the main function to use for all main windows
    """
    # First, maximize the window
    maximize_window(window)
    
    # Then, ensure it's centered (for Linux fallback)
    window.after(100, lambda: center_window(window))
    window.after(300, lambda: center_window(window))
    window.after(600, lambda: center_window(window))


def set_fullscreen(window):
    """
    Set a window to TRUE fullscreen (no title bar, no taskbar)
    Use this only if you want a true kiosk-style fullscreen
    """
    window.attributes('-fullscreen', True)


def set_maximized(window):
    """
    Set a window to maximized state (with title bar and taskbar visible)
    This is the standard "maximize" button behavior
    """
    if sys.platform.startswith('win'):
        window.state('zoomed')
    else:
        # Linux fallback
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window.geometry(f"{screen_width}x{screen_height}+0+0")