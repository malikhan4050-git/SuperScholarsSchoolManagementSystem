"""
Window Manager - Cross-platform maximized window sizing
Reserves space for the taskbar (Windows & Linux)
"""

import sys


# Constant taskbar height (in pixels)
# Windows 10/11 taskbar is 40px (default) or up to 48px (large icons)
# Linux (GNOME/KDE) taskbars are usually 40-48px
TASKBAR_HEIGHT = 73


def apply_fullscreen(window):
    """
    Size the window to fill the screen MINUS taskbar height.
    Works on both Windows and Linux.
    Window is locked (not resizable).
    """
    # Prevent user from resizing
    window.resizable(False, False)
    
    # Apply geometry with multiple attempts for reliability
    window.after(50, lambda: _apply_geometry(window))
    window.after(200, lambda: _apply_geometry(window))
    window.after(500, lambda: _apply_geometry(window))


def _apply_geometry(window):
    """Internal helper to set window size accounting for taskbar"""
    try:
        window.update_idletasks()
        
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calculate window size (subtract taskbar space)
        window_width = screen_width
        window_height = screen_height - TASKBAR_HEIGHT
        
        # Position at top-left, leaving room for taskbar at bottom
        window.geometry(f"{window_width}x{window_height}+0+0")
    except Exception:
        pass