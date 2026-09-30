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
from app.utils.window_manager import apply_fullscreen

class PrincipalDashboard(ctk.CTk):
    """Principal Dashboard Class - View Only Access"""
    
    def __init__(self, user):
        super().__init__()
        
        # Store current user
        self.current_user = user
        
        # Configure window
        self.title("Super Scholars - Principal Dashboard")
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Apply fullscreen sizing
        apply_fullscreen(self)
        
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
        
        # ===== HEADER =====
        self.header_frame = ctk.CTkFrame(
            self.main_content,
            height=80,
            fg_color="white",
            corner_radius=0
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Dashboard Overview",
            font=("Arial", 26, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=25)
        
        # ===== WELCOME SECTION =====
        welcome_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=15
        )
        welcome_frame.pack(fill="x", padx=25, pady=(15, 10))
        
        welcome_title = ctk.CTkLabel(
            welcome_frame,
            text=f"Welcome back, {self.current_user.full_name}!",
            font=("Arial", 20, "bold"),
            text_color="#1e3a5f"
        )
        welcome_title.pack(anchor="w", padx=25, pady=(20, 5))
        
        welcome_subtitle = ctk.CTkLabel(
            welcome_frame,
            text="Here's an overview of your school's current status",
            font=("Arial", 13),
            text_color="#7f8c8d"
        )
        welcome_subtitle.pack(anchor="w", padx=25, pady=(0, 20))
        
        # ===== STATS SECTION =====
        total_students = self.db.query(Student).count()
        total_families = self.db.query(Guardian).count()
        total_teachers = self.db.query(Teacher).count()
        
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
            {
                "title": "Total Students",
                "value": str(total_students),
                "icon": "STU",
                "color": "#3498db",
                "bg": "#ebf5fb"
            },
            {
                "title": "Total Teachers",
                "value": str(total_teachers),
                "icon": "TCH",
                "color": "#27ae60",
                "bg": "#e8f8f5"
            },
            {
                "title": "Total Families",
                "value": str(total_families),
                "icon": "FAM",
                "color": "#e74c3c",
                "bg": "#fdedec"
            },
            {
                "title": "Pending Challans",
                "value": str(pending_challans),
                "icon": "PEN",
                "color": "#9b59b6",
                "bg": "#f4ecf7"
            },
            {
                "title": "Total Collected",
                "value": f"Rs. {total_collected:,.0f}",
                "icon": "COL",
                "color": "#27ae60",
                "bg": "#e8f8f5"
            },
            {
                "title": "Outstanding",
                "value": f"Rs. {total_outstanding:,.0f}",
                "icon": "OUT",
                "color": "#e67e22",
                "bg": "#fef5e7"
            }
        ]
        
        # Container for stat cards
        stats_container = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        stats_container.pack(fill="x", padx=25, pady=15)
        
        # Configure 6 equal columns
        for i in range(6):
            stats_container.grid_columnconfigure(i, weight=1)
        
        # Create each stat card
        for i, stat in enumerate(stats):
            card = ctk.CTkFrame(
                stats_container,
                fg_color="white",
                corner_radius=15,
                height=160
            )
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            card.grid_propagate(False)
            
            inner = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            inner.pack(fill="both", expand=True, padx=15, pady=18)
            
            icon_box = ctk.CTkFrame(
                inner,
                width=44,
                height=44,
                corner_radius=12,
                fg_color=stat["bg"]
            )
            icon_box.pack(anchor="w")
            icon_box.pack_propagate(False)
            
            icon_label = ctk.CTkLabel(
                icon_box,
                text=stat["icon"],
                font=("Arial", 12, "bold"),
                text_color=stat["color"]
            )
            icon_label.pack(expand=True)
            
            value_label = ctk.CTkLabel(
                inner,
                text=stat["value"],
                font=("Arial", 20, "bold"),
                text_color=stat["color"]
            )
            value_label.pack(anchor="w", pady=(15, 2))
            
            title_label = ctk.CTkLabel(
                inner,
                text=stat["title"],
                font=("Arial", 12),
                text_color="#7f8c8d"
            )
            title_label.pack(anchor="w")
        
        # ===== BOTTOM SPACER =====
        bottom_spacer = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent",
            height=20
        )
        bottom_spacer.pack(fill="x")
    
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