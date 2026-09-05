"""
Login Window for Super Scholars School Management System
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal
from app.utils.auth import Authentication
from app.utils.center_window import center_window, center_and_maximize

class LoginWindow(ctk.CTk):
    """Login Window Class"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Super Scholars School Management System")
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # UI fix: Center and maximize window after creation
        self.after(100, lambda: center_and_maximize(self))
        
        # Initialize authentication
        self.db = SessionLocal()
        self.auth = Authentication(self.db)
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        """Create all widgets for login window"""
        
        # Main container with two columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Left Panel (Branding)
        self.left_panel = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#1e3a5f"
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        
        # System Title
        self.title_label = ctk.CTkLabel(
            self.left_panel,
            text="SUPER SCHOLARS",
            font=("Arial", 28, "bold"),
            text_color="white"
        )
        self.title_label.pack(pady=(80, 10))
        
        self.subtitle_label = ctk.CTkLabel(
            self.left_panel,
            text="School Management System",
            font=("Arial", 16),
            text_color="#a0b4c8"
        )
        self.subtitle_label.pack(pady=(0, 40))
        
        # Additional info
        self.info_frame = ctk.CTkFrame(
            self.left_panel,
            fg_color="transparent"
        )
        self.info_frame.pack(pady=20)
        
        info_items = [
            "Fee Management",
            "Student Records",
            "Guardian Tracking",
            "Financial Reports"
        ]
        
        for item in info_items:
            label = ctk.CTkLabel(
                self.info_frame,
                text=item,
                font=("Arial", 14),
                text_color="#a0b4c8"
            )
            label.pack(anchor="w", pady=5)
        
        # Right Panel (Login Form)
        self.right_panel = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="white"
        )
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Login Form Container
        self.form_frame = ctk.CTkFrame(
            self.right_panel,
            width=400,
            fg_color="transparent"
        )
        self.form_frame.pack(expand=True)
        
        # Login Header
        self.login_title = ctk.CTkLabel(
            self.form_frame,
            text="Welcome Back!",
            font=("Arial", 32, "bold"),
            text_color="#1e3a5f"
        )
        self.login_title.pack(pady=(0, 10))
        
        self.login_subtitle = ctk.CTkLabel(
            self.form_frame,
            text="Please login to continue",
            font=("Arial", 14),
            text_color="gray"
        )
        self.login_subtitle.pack(pady=(0, 40))
        
        # Username Entry
        self.username_label = ctk.CTkLabel(
            self.form_frame,
            text="Username",
            font=("Arial", 14, "bold"),
            text_color="#1e3a5f"
        )
        self.username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            self.form_frame,
            width=350,
            height=45,
            placeholder_text="Enter username",
            font=("Arial", 14),
            border_color="#1e3a5f",
            corner_radius=8
        )
        self.username_entry.pack(pady=(0, 20))
        
        # Password Entry
        self.password_label = ctk.CTkLabel(
            self.form_frame,
            text="Password",
            font=("Arial", 14, "bold"),
            text_color="#1e3a5f"
        )
        self.password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            self.form_frame,
            width=350,
            height=45,
            placeholder_text="Enter password",
            font=("Arial", 14),
            show="*",
            border_color="#1e3a5f",
            corner_radius=8
        )
        self.password_entry.pack(pady=(0, 20))
        
        # Login Button
        self.login_button = ctk.CTkButton(
            self.form_frame,
            text="Login",
            width=350,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color="#1e3a5f",
            hover_color="#2c5282",
            corner_radius=8,
            command=self.login
        )
        self.login_button.pack(pady=(20, 10))
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            font=("Arial", 12),
            text_color="red"
        )
        self.status_label.pack(pady=(10, 0))
        
        # Bind Enter key
        self.bind('<Return>', lambda event: self.login())
        
    def login(self):
        """Handle login functionality"""
        
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.status_label.configure(text="Please enter username and password")
            return
        
        # Authenticate
        result = self.auth.login(username, password)
        
        if result["success"]:
            self.status_label.configure(text="", text_color="green")
            
            # Get user role
            user = result["user"]
            role = user.role.value
            
            # Show success message
            self.status_label.configure(text="Login successful!")
            self.after(500, lambda: self.open_dashboard(role, user))
        else:
            self.status_label.configure(text=f"{result['message']}", text_color="red")
    
    def open_dashboard(self, role, user):
        """Open the appropriate dashboard based on role"""
        
        self.destroy()
        
        # Import dashboard based on role
        if role == "super_admin":
            from app.ui.super_admin_dashboard import SuperAdminDashboard
            dashboard = SuperAdminDashboard(user)
        elif role == "admin":
            from app.ui.admin_dashboard import AdminDashboard
            dashboard = AdminDashboard(user)
        elif role == "principal":
            from app.ui.principal_dashboard import PrincipalDashboard
            dashboard = PrincipalDashboard(user)
        else:
            messagebox.showerror("Error", "Invalid role!")
            return
        
        dashboard.mainloop()
    
    def on_closing(self):
        """Handle window close event"""
        self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()