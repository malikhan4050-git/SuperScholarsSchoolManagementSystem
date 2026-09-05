"""
Admin Dashboard for Super Scholars School Management System
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal, Student, Teacher, FeeRecord, FeeStatus, Guardian
from app.utils.auth import Authentication
from app.services.student_service import StudentService
from app.services.fee_service import FeeService
from app.ui.student_form import StudentRegistrationForm
from app.ui.fee_challan_screen import FeeChallanlScreen
from app.ui.promotion_screen import PromotionScreen
from app.utils.center_window import center_and_maximize

class AdminDashboard(ctk.CTk):
    """Admin Dashboard Class"""
    
    def __init__(self, user):
        super().__init__()
        
        # Store current user
        self.current_user = user
        
        # Configure window
        self.title("Super Scholars - Admin Dashboard")
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Center and maximize window after creation
        self.after(100, lambda: center_and_maximize(self))
        
        # Initialize database
        self.db = SessionLocal()
        self.auth = Authentication(self.db)
        self.auth.current_user = user
        self.student_service = StudentService(self.db)
        self.fee_service = FeeService(self.db)
        
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
        self.sidebar.grid_propagate(False)
        
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
            text="Admin",
            font=("Arial", 12),
            text_color="#a0b4c8"
        )
        self.user_role.pack(pady=(0, 10))
        
        # Navigation buttons
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Students", self.show_students),
            ("Promote Students", self.show_promotion),
            ("Fee Management", self.show_fees),
            ("Record Payment", self.show_payments),
            ("Reports", self.show_reports),
            ("Settings", self.show_settings)
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
        
        # Header
        self.header_frame = ctk.CTkFrame(
            self.main_content,
            height=70,
            fg_color="white",
            corner_radius=0
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Dashboard Overview",
            font=("Arial", 22, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=25, pady=20)
        
        # Stats Container - Single Row with Professional Cards
        self.create_stats_cards()
    
    def create_stats_cards(self):
        """Create professional stats cards in a single row"""
        
        # Get actual stats
        total_students = self.db.query(Student).count()
        total_fees_pending = self.db.query(FeeRecord).filter(
            FeeRecord.status == FeeStatus.PENDING
        ).count()
        
        # Fee summary
        fee_summary = self.fee_service.get_fee_summary()
        
        # Stats data - (title, value, icon_color, bg_color, accent_color)
        stats = [
            {
                "title": "Total Students",
                "value": str(total_students),
                "icon": "STU",
                "color": "#3498db",
                "bg": "#ebf5fb",
                "border": "#3498db"
            },
            {
                "title": "Pending Fees",
                "value": str(total_fees_pending),
                "icon": "PEN",
                "color": "#e74c3c",
                "bg": "#fdedec",
                "border": "#e74c3c"
            },
            {
                "title": "Total Collected",
                "value": f"Rs. {fee_summary['total_collected']:,.0f}",
                "icon": "COL",
                "color": "#27ae60",
                "bg": "#e8f8f5",
                "border": "#27ae60"
            },
            {
                "title": "Outstanding",
                "value": f"Rs. {fee_summary['total_outstanding']:,.0f}",
                "icon": "OUT",
                "color": "#f39c12",
                "bg": "#fef5e7",
                "border": "#f39c12"
            }
        ]
        
        # Container for cards
        stats_container = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        stats_container.pack(fill="x", padx=25, pady=20)
        
        # Configure grid - 4 columns, all equal weight
        for i in range(4):
            stats_container.grid_columnconfigure(i, weight=1)
        
        # Create each card
        for i, stat in enumerate(stats):
            self.create_stat_card(stats_container, stat, i)
    
    def create_stat_card(self, parent, stat, column):
        """Create a single professional stat card"""
        
        # Card frame with border
        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=12,
            border_width=2,
            border_color=stat["border"],
            height=110
        )
        card.grid(row=0, column=column, padx=8, pady=8, sticky="nsew")
        card.grid_propagate(False)
        
        # Icon circle (colored background with text)
        icon_frame = ctk.CTkFrame(
            card,
            width=45,
            height=45,
            corner_radius=22,
            fg_color=stat["bg"]
        )
        icon_frame.pack(pady=(10, 3))
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=stat["icon"],
            font=("Arial", 12, "bold"),
            text_color=stat["color"]
        )
        icon_label.pack(expand=True)
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=stat["value"],
            font=("Arial", 20, "bold"),
            text_color=stat["color"]
        )
        value_label.pack(pady=(2, 1))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=stat["title"],
            font=("Arial", 11),
            text_color="#7f8c8d"
        )
        title_label.pack(pady=(0, 8))
    
    def show_students(self):
        """Show student management view"""
        self.clear_main_content()
        
        # Header
        self.header_frame = ctk.CTkFrame(
            self.main_content,
            height=100,
            fg_color="white",
            corner_radius=0
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Student Management",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        # Add Student Button
        self.add_student_btn = ctk.CTkButton(
            self.header_frame,
            text="+ Add Student",
            width=150,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.show_add_student_form
        )
        self.add_student_btn.pack(side="right", padx=30, pady=20)
        
        # Search Frame
        self.search_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=10
        )
        self.search_frame.pack(fill="x", padx=30, pady=20)
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            width=300,
            height=35,
            placeholder_text="Search by name or ID...",
            font=("Arial", 13)
        )
        self.search_entry.pack(side="left", padx=20, pady=10)
        
        self.search_btn = ctk.CTkButton(
            self.search_frame,
            text="Search",
            width=100,
            height=35,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.search_students
        )
        self.search_btn.pack(side="left", padx=10, pady=10)
        
        # Students list frame
        self.students_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=10
        )
        self.students_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Refresh students list
        self.refresh_students_list()
    
    def show_promotion(self):
        """Show student promotion screen"""
        self.clear_main_content()
        
        try:
            self.promotion_screen = PromotionScreen(self.main_content, self.db, self.student_service)
            self.promotion_screen.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Promotion screen: {str(e)}")
            
            self.header_frame = ctk.CTkFrame(
                self.main_content,
                height=100,
                fg_color="white",
                corner_radius=0
            )
            self.header_frame.pack(fill="x")
            self.header_frame.pack_propagate(False)
            
            self.header_title = ctk.CTkLabel(
                self.header_frame,
                text="Student Promotion",
                font=("Arial", 24, "bold"),
                text_color="#1e3a5f"
            )
            self.header_title.pack(side="left", padx=30, pady=30)
            
            placeholder = ctk.CTkLabel(
                self.main_content,
                text="Promotion features coming soon...",
                font=("Arial", 18),
                text_color="gray"
            )
            placeholder.pack(pady=100)
    
    def show_add_student_form(self):
        """Show the new professional student registration form"""
        form = StudentRegistrationForm(self, self.student_service)
        self.wait_window(form)
        self.refresh_students_list()
    
    def edit_student(self, student_id):
        """Edit student details"""
        student = self.student_service.get_student_by_id(student_id)
        if student:
            form = StudentRegistrationForm(self, self.student_service, student=student)
            self.wait_window(form)
            self.refresh_students_list()
        else:
            messagebox.showerror("Error", "Student not found!")
    
    def refresh_students_list(self, students=None):
        """Refresh the students list"""
        for widget in self.students_frame.winfo_children():
            widget.destroy()
        
        list_title = ctk.CTkLabel(
            self.students_frame,
            text="All Students",
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        list_title.pack(pady=10)
        
        if students is None:
            students = self.student_service.get_all_students()
        
        if not students:
            empty_label = ctk.CTkLabel(
                self.students_frame,
                text="No students found. Click 'Add Student' to create one.",
                font=("Arial", 14),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        
        scroll_frame = ctk.CTkScrollableFrame(
            self.students_frame,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for student in students:
            student_card = ctk.CTkFrame(
                scroll_frame,
                fg_color="#f8f9fa",
                corner_radius=8
            )
            student_card.pack(fill="x", padx=10, pady=5)
            
            guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
            family_id = guardian.family_id if guardian else "N/A"
            
            info_text = f"{student.full_name} | ID: {student.student_id} | Family: {family_id} | Class: {student.class_grade}"
            
            student_label = ctk.CTkLabel(
                student_card,
                text=info_text,
                font=("Arial", 13),
                text_color="#2c3e50"
            )
            student_label.pack(side="left", padx=15, pady=10)
            
            view_btn = ctk.CTkButton(
                student_card,
                text="View",
                width=80,
                height=30,
                fg_color="#3498db",
                hover_color="#2980b9",
                command=lambda sid=student.id: self.view_student(sid)
            )
            view_btn.pack(side="right", padx=5, pady=5)
            
            edit_btn = ctk.CTkButton(
                student_card,
                text="Edit",
                width=80,
                height=30,
                fg_color="#f39c12",
                hover_color="#e67e22",
                command=lambda sid=student.id: self.edit_student(sid)
            )
            edit_btn.pack(side="right", padx=5, pady=5)
            
            delete_btn = ctk.CTkButton(
                student_card,
                text="Delete",
                width=80,
                height=30,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                command=lambda sid=student.id: self.delete_student(sid)
            )
            delete_btn.pack(side="right", padx=5, pady=5)
    
    def search_students(self):
        """Search for students"""
        search_term = self.search_entry.get().strip()
        if search_term:
            results = self.student_service.search_students(search_term)
            self.refresh_students_list(results)
        else:
            self.refresh_students_list()
    
    def view_student(self, student_id):
        """View student details"""
        student = self.student_service.get_student_by_id(student_id)
        if student:
            guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
            family_id = guardian.family_id if guardian else "N/A"
            
            messagebox.showinfo("Student Details", 
                f"Name: {student.full_name}\n"
                f"ID: {student.student_id}\n"
                f"Family ID: {family_id}\n"
                f"Class: {student.class_grade}\n"
                f"Monthly Fee: Rs. {student.monthly_tuition_fee:,.0f}\n"
                f"Concession: Rs. {student.fee_concession:,.0f}")
    
    def delete_student(self, student_id):
        """Delete a student"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            result = self.student_service.delete_student(student_id)
            if result["success"]:
                messagebox.showinfo("Success", "Student deleted successfully!")
                self.refresh_students_list()
            else:
                messagebox.showerror("Error", result["message"])
    
    def show_fees(self):
        """Show fee management view"""
        self.clear_main_content()
        
        try:
            self.fee_challan_screen = FeeChallanlScreen(self.main_content, self.db)
            self.fee_challan_screen.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Fee Challan screen: {str(e)}")
            
            self.header_frame = ctk.CTkFrame(
                self.main_content,
                height=100,
                fg_color="white",
                corner_radius=0
            )
            self.header_frame.pack(fill="x")
            self.header_frame.pack_propagate(False)
            
            self.header_title = ctk.CTkLabel(
                self.header_frame,
                text="Fee Management",
                font=("Arial", 24, "bold"),
                text_color="#1e3a5f"
            )
            self.header_title.pack(side="left", padx=30, pady=30)
            
            placeholder = ctk.CTkLabel(
                self.main_content,
                text="Fee Management features coming soon...",
                font=("Arial", 18),
                text_color="gray"
            )
            placeholder.pack(pady=100)
    
    def show_payments(self):
        """Show Record Payment screen"""
        self.clear_main_content()
        
        from app.ui.record_payment_screen import RecordPaymentScreen
        self.record_payment_screen = RecordPaymentScreen(self.main_content, self.db)
        self.record_payment_screen.pack(fill="both", expand=True)
    
    def show_reports(self):
        """Show reports view"""
        self.clear_main_content()
        
        self.header_frame = ctk.CTkFrame(
            self.main_content,
            height=100,
            fg_color="white",
            corner_radius=0
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Reports",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        placeholder = ctk.CTkLabel(
            self.main_content,
            text="Reports features coming soon...",
            font=("Arial", 18),
            text_color="gray"
        )
        placeholder.pack(pady=100)
    
    def show_settings(self):
        """Show settings view"""
        self.clear_main_content()
        
        self.header_frame = ctk.CTkFrame(
            self.main_content,
            height=100,
            fg_color="white",
            corner_radius=0
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Settings",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        placeholder = ctk.CTkLabel(
            self.main_content,
            text="Settings features coming soon...",
            font=("Arial", 18),
            text_color="gray"
        )
        placeholder.pack(pady=100)
    
    def logout(self):
        """Logout from the system"""
        if messagebox.askyesno("Confirm", "Are you sure you want to logout?"):
            self.auth.logout()
            self.db.close()
            self.destroy()
            
            from app.ui.login_window import LoginWindow
            login_window = LoginWindow()
            login_window.mainloop()

if __name__ == "__main__":
    from app.database.models import SessionLocal, User, UserRole
    db = SessionLocal()
    user = db.query(User).filter(User.role == UserRole.ADMIN).first()
    db.close()
    
    if user:
        app = AdminDashboard(user)
        app.mainloop()