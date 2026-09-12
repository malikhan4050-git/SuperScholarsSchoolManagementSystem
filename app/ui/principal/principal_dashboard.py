"""
Principal Dashboard - Main Navigation
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from sqlalchemy import func

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.database.models import SessionLocal, Guardian, Student, Teacher, FeeChallan
from app.utils.auth import Authentication
from app.ui.principal.principal_students import PrincipalStudentsView
from app.ui.principal.principal_fees import PrincipalFeesView
from app.ui.principal.principal_reports import PrincipalReportsView

class PrincipalDashboard(ctk.CTk):
    """Principal Dashboard Class - View Only Access"""
    
    def __init__(self, user):
        super().__init__()
        
        # Store current user
        self.current_user = user
        
        # Configure window
        self.title("Super Scholars - Principal Dashboard")
        self.geometry("1400x800")
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Initialize database
        self.db = SessionLocal()
        self.auth = Authentication(self.db)
        self.auth.current_user = user
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        """Create main dashboard layout"""
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
    def create_sidebar(self):
        """Create sidebar navigation"""
        
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color="#1e3a5f"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="SUPER\nSCHOLARS",
            font=("Arial", 20, "bold"),
            text_color="white",
            justify="center"
        )
        self.logo_label.pack(pady=(30, 40))
        
        # User info frame
        self.user_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="#2c5282",
            corner_radius=10
        )
        self.user_frame.pack(padx=20, pady=(0, 30), fill="x")
        
        self.user_name = ctk.CTkLabel(
            self.user_frame,
            text=f"{self.current_user.full_name}",
            font=("Arial", 14, "bold"),
            text_color="white"
        )
        self.user_name.pack(pady=10)
        
        self.user_role = ctk.CTkLabel(
            self.user_frame,
            text="Principal",
            font=("Arial", 12),
            text_color="#a0b4c8"
        )
        self.user_role.pack(pady=(0, 10))
        
        # Navigation buttons
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Students", self.show_students),
            ("Fees", self.show_fees),
            ("Reports", self.show_reports)
        ]
        
        for text, command in nav_items:
            button = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=200,
                height=40,
                font=("Arial", 14),
                fg_color="transparent",
                hover_color="#2c5282",
                anchor="w",
                command=command
            )
            button.pack(padx=20, pady=5)
        
        # Logout button
        self.logout_button = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            width=200,
            height=40,
            font=("Arial", 14),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.logout
        )
        self.logout_button.pack(side="bottom", padx=20, pady=20)
        
    def create_main_content(self):
        """Create main content area"""
        
        self.main_content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#f0f2f5"
        )
        self.main_content.grid(row=0, column=1, sticky="nsew")
        
        # Initialize with dashboard
        self.show_dashboard()
        
    def clear_main_content(self):
        """Clear main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.clear_main_content()
        
        # Create dashboard view
        dashboard_view = ctk.CTkFrame(self.main_content, fg_color="#f0f2f5")
        dashboard_view.pack(fill="both", expand=True)
        
        # Header
        self.header_frame = ctk.CTkFrame(
            dashboard_view,
            height=100,
            fg_color="white",
            corner_radius=0
        )
        self.header_frame.pack(fill="x")
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Dashboard Overview",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        # Stats cards
        self.stats_frame = ctk.CTkFrame(
            dashboard_view,
            fg_color="transparent"
        )
        self.stats_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Get actual stats
        total_students = self.db.query(Student).count()
        total_families = self.db.query(Guardian).count()
        total_teachers = self.db.query(Teacher).count()
        
        # Calculate from FeeChallan
        total_collected = self.db.query(FeeChallan).with_entities(
            func.sum(FeeChallan.paid_amount)
        ).scalar() or 0
        
        total_outstanding = self.db.query(FeeChallan).with_entities(
            func.sum(FeeChallan.remaining_amount)
        ).scalar() or 0
        
        pending_challans = self.db.query(FeeChallan).filter(
            FeeChallan.is_paid == False
        ).count()
        
        stats = [
            ("Total Students", total_students, "#3498db"),
            ("Total Teachers", total_teachers, "#2ecc71"),
            ("Total Families", total_families, "#e74c3c"),
            ("Pending Challans", pending_challans, "#9b59b6"),
            ("Total Collected", f"Rs. {total_collected:,.0f}", "#f39c12"),
            ("Outstanding", f"Rs. {total_outstanding:,.0f}", "#e67e22")
        ]
        
        # Make 6 cards fit
        for i in range(6):
            self.stats_frame.grid_columnconfigure(i, weight=1)
        
        for i, (title, value, color) in enumerate(stats):
            card = ctk.CTkFrame(
                self.stats_frame,
                width=180,
                height=150,
                fg_color="white",
                corner_radius=15
            )
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            
            value_label = ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 24, "bold"),
                text_color=color
            )
            value_label.pack(pady=(30, 5))
            
            title_label = ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 14),
                text_color="gray"
            )
            title_label.pack(pady=(0, 30))
    
    def show_students(self):
        """Show students view"""
        self.clear_main_content()
        
        # Create students view
        students_view = PrincipalStudentsView(self.main_content, self.db)
        students_view.pack(fill="both", expand=True)
    
    def show_fees(self):
        """Show fees view"""
        self.clear_main_content()
        
        # Create fees view
        fees_view = PrincipalFeesView(self.main_content, self.db)
        fees_view.pack(fill="both", expand=True)
    
    def show_reports(self):
        """Show reports view"""
        self.clear_main_content()
        
        # Create reports view
        reports_view = PrincipalReportsView(self.main_content, self.db)
        reports_view.pack(fill="both", expand=True)
    
    def logout(self):
        """Logout from the system"""
        if messagebox.askyesno("Confirm", "Are you sure you want to logout?"):
            self.auth.logout()
            self.db.close()
            self.destroy()
            
            # Import and show login window
            from app.ui.login_window import LoginWindow
            login_window = LoginWindow()
            login_window.mainloop()

if __name__ == "__main__":
    # Test with a dummy user
    from app.database.models import SessionLocal, User, UserRole
    db = SessionLocal()
    user = db.query(User).filter(User.role == UserRole.PRINCIPAL).first()
    db.close()
    
    if user:
        app = PrincipalDashboard(user)
        app.mainloop()