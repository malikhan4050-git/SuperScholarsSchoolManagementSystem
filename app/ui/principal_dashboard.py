"""
Principal Dashboard for Super Scholars School Management System
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal, Guardian, Student, FeeRecord, FeeStatus, Teacher
from app.utils.auth import Authentication
from app.services.fee_service import FeeService
from app.utils.center_window import center_and_maximize

class PrincipalDashboard(ctk.CTk):
    """Principal Dashboard Class"""
    
    def __init__(self, user):
        super().__init__()
        
        self.current_user = user
        
        self.title("Super Scholars - Principal Dashboard")
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.after(100, lambda: center_and_maximize(self))
        
        self.db = SessionLocal()
        self.auth = Authentication(self.db)
        self.auth.current_user = user
        self.fee_service = FeeService(self.db)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create main dashboard layout"""
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
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
        
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="SUPER\nSCHOLARS",
            font=("Arial", 20, "bold"),
            text_color="white",
            justify="center"
        )
        self.logo_label.pack(pady=(30, 40))
        
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
        
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Students", self.show_students),
            ("Teachers", self.show_teachers),
            ("Fees", self.show_fees),
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
        
        self.show_dashboard()
        
    def clear_main_content(self):
        """Clear main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.clear_main_content()
        
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
        
        self.create_stats_cards()
    
    def create_stats_cards(self):
        """Create professional stats cards in a single row"""
        
        total_students = self.db.query(Student).count()
        total_teachers = self.db.query(Teacher).count()
        total_families = self.db.query(Guardian).count()
        
        fee_summary = self.fee_service.get_fee_summary()
        
        stats = [
            {
                "title": "Total Students",
                "value": str(total_students),
                "icon": "🎓",
                "color": "#3498db",
                "bg": "#ebf5fb",
                "border": "#3498db"
            },
            {
                "title": "Total Teachers",
                "value": str(total_teachers),
                "icon": "👨‍🏫",
                "color": "#27ae60",
                "bg": "#e8f8f5",
                "border": "#27ae60"
            },
            {
                "title": "Total Families",
                "value": str(total_families),
                "icon": "🏠",
                "color": "#e74c3c",
                "bg": "#fdedec",
                "border": "#e74c3c"
            },
            {
                "title": "Collected",
                "value": f"Rs. {fee_summary['total_collected']:,.0f}",
                "icon": "💰",
                "color": "#f39c12",
                "bg": "#fef5e7",
                "border": "#f39c12"
            }
        ]
        
        stats_container = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        stats_container.pack(fill="x", padx=25, pady=20)
        
        for i in range(4):
            stats_container.grid_columnconfigure(i, weight=1)
        
        for i, stat in enumerate(stats):
            self.create_stat_card(stats_container, stat, i)
    
    def create_stat_card(self, parent, stat, column):
        """Create a single professional stat card"""
        
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
            font=("Arial", 20),
            text_color=stat["color"]
        )
        icon_label.pack(expand=True)
        
        value_label = ctk.CTkLabel(
            card,
            text=stat["value"],
            font=("Arial", 20, "bold"),
            text_color=stat["color"]
        )
        value_label.pack(pady=(2, 1))
        
        title_label = ctk.CTkLabel(
            card,
            text=stat["title"],
            font=("Arial", 11),
            text_color="#7f8c8d"
        )
        title_label.pack(pady=(0, 8))
    
    def show_students(self):
        """Show students view (Read Only)"""
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
            text="Student Management (View Only)",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        self.students_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=10
        )
        self.students_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.refresh_students_list()
    
    def refresh_students_list(self):
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
        
        students = self.db.query(Student).all()
        
        if not students:
            empty_label = ctk.CTkLabel(
                self.students_frame,
                text="No students found.",
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
    
    def view_student(self, student_id):
        """View student details"""
        student = self.db.query(Student).filter(Student.id == student_id).first()
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
    
    def show_teachers(self):
        """Show teachers view"""
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
            text="Teacher Management",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        self.teachers_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=10
        )
        self.teachers_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.refresh_teachers_list()
    
    def refresh_teachers_list(self):
        """Refresh the teachers list"""
        for widget in self.teachers_frame.winfo_children():
            widget.destroy()
        
        list_title = ctk.CTkLabel(
            self.teachers_frame,
            text="All Teachers",
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        list_title.pack(pady=10)
        
        teachers = self.db.query(Teacher).all()
        
        if not teachers:
            empty_label = ctk.CTkLabel(
                self.teachers_frame,
                text="No teachers found.",
                font=("Arial", 14),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        
        scroll_frame = ctk.CTkScrollableFrame(
            self.teachers_frame,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for teacher in teachers:
            teacher_card = ctk.CTkFrame(
                scroll_frame,
                fg_color="#f8f9fa",
                corner_radius=8
            )
            teacher_card.pack(fill="x", padx=10, pady=5)
            
            info_text = f"{teacher.full_name} | {teacher.department} | {teacher.status}"
            
            teacher_label = ctk.CTkLabel(
                teacher_card,
                text=info_text,
                font=("Arial", 13),
                text_color="#2c3e50"
            )
            teacher_label.pack(side="left", padx=15, pady=10)
    
    def show_fees(self):
        """Show fees view (View Only)"""
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
            text="Fee Management (View Only)",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        summary_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=10
        )
        summary_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        fee_summary = self.fee_service.get_fee_summary()
        
        summary_text = f"""
        Fee Summary:
        ============
        Total Billed:    Rs. {fee_summary['total_billed']:,.0f}
        Total Collected: Rs. {fee_summary['total_collected']:,.0f}
        Total Outstanding: Rs. {fee_summary['total_outstanding']:,.0f}
        """
        
        summary_label = ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=("Arial", 16),
            text_color="#1e3a5f",
            justify="left"
        )
        summary_label.pack(pady=50)
    
    def show_reports(self):
        """Show reports view"""
        self.clear_main_content()
        
        header = ctk.CTkLabel(
            self.main_content,
            text="Reports & Analytics",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        header.pack(pady=100)
    
    def show_settings(self):
        """Show settings view"""
        self.clear_main_content()
        
        header = ctk.CTkLabel(
            self.main_content,
            text="Settings",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        header.pack(pady=100)
    
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
    user = db.query(User).filter(User.role == UserRole.PRINCIPAL).first()
    db.close()
    
    if user:
        app = PrincipalDashboard(user)
        app.mainloop()