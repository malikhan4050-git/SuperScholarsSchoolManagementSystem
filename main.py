"""
Super Scholars School Management System
Main Entry Point
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.init_db import setup_database
from app.ui.login_window import LoginWindow

def main():
    """Main application entry point"""
    
    print("=" * 60)
    print("SUPER SCHOLARS SCHOOL MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Setup database on first run
    if not os.path.exists("super_scholars.db"):
        print("\n📦 First time setup detected...")
        setup_database()
    
    # Launch the login window
    print("\n🚀 Launching application...")
    app = LoginWindow()
    app.mainloop()

if __name__ == "__main__":
    main()