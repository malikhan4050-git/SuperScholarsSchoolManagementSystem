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
            width=220,
            corner_radius=0,
            fg_color="#1e3a5f"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="SUPER\nSCHOLARS",
            font=("Arial", 18, "bold"),
            text_color="white",
            justify="center"
        )
        self.logo_label.pack(pady=(25, 30))
        
        # User info frame
        self.user_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="#2c5282",
            corner_radius=8
        )
        self.user_frame.pack(padx=15, pady=(0, 20), fill="x")
        
        self.user_name = ctk.CTkLabel(
            self.user_frame,
            text=f"{self.current_user.full_name}",
            font=("Arial", 13, "bold"),
            text_color="white"
        )
        self.user_name.pack(pady=8)
        
        self.user_role = ctk.CTkLabel(
            self.user_frame,
            text="Admin",
            font=("Arial", 11),
            text_color="#a0b4c8"
        )
        self.user_role.pack(pady=(0, 8))
        
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
                width=180,
                height=38,
                font=("Arial", 13),
                fg_color="transparent",
                hover_color="#2c5282",
                anchor="w",
                command=command
            )
            button.pack(padx=15, pady=3)
        
        # Logout button
        self.logout_button = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            width=180,
            height=38,
            font=("Arial", 13),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.logout
        )
        self.logout_button.pack(side="bottom", padx=15, pady=15)
        
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
        total_fees_pending = self.db.query(FeeRecord).filter(
            FeeRecord.status == FeeStatus.PENDING
        ).count()
        
        fee_summary = self.fee_service.get_fee_summary()
        
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
            font=("Arial", 12, "bold"),
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
        """Show student management view - Professional Table"""
        self.clear_main_content()
        
        # ===== HEADER SECTION =====
        self.header_frame = ctk.CTkFrame(
            self.main_content,
            height=65,
            fg_color="white",
            corner_radius=0
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Student Management",
            font=("Arial", 20, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=20, pady=18)
        
        # Add Student Button
        self.add_student_btn = ctk.CTkButton(
            self.header_frame,
            text="+ Add Student",
            width=120,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#27ae60",
            hover_color="#229954",
            corner_radius=6,
            command=self.show_add_student_form
        )
        self.add_student_btn.pack(side="right", padx=20, pady=15)
        
        # ===== SEARCH BAR SECTION =====
        self.search_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent",
            height=48
        )
        self.search_frame.pack(fill="x", padx=20, pady=(10, 5))
        self.search_frame.pack_propagate(False)
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search by student name, ID, or family ID...",
            font=("Arial", 12),
            height=35,
            border_color="#d5d8dc",
            fg_color="white",
            corner_radius=6
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self.search_students())
        
        self.search_btn = ctk.CTkButton(
            self.search_frame,
            text="Search",
            font=("Arial", 11, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            width=80,
            height=35,
            corner_radius=6,
            command=self.search_students
        )
        self.search_btn.pack(side="left", padx=(0, 8))
        
        self.clear_btn = ctk.CTkButton(
            self.search_frame,
            text="Clear",
            font=("Arial", 11, "bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            width=65,
            height=35,
            corner_radius=6,
            command=self.clear_search
        )
        self.clear_btn.pack(side="left")
        
        # ===== TABLE SECTION =====
        self.students_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#e0e0e0"
        )
        self.students_frame.pack(fill="both", expand=True, padx=20, pady=(8, 15))
        
        # Refresh students list
        self.refresh_students_list()
    
    def refresh_students_list(self, students=None):
        """Refresh the students list - Proper Table Layout (No Scrollbar)"""
        
        # Clear existing content
        for widget in self.students_frame.winfo_children():
            widget.destroy()
        
        # Get students
        if students is None:
            students = self.student_service.get_all_students()
        
        if not students:
            empty_frame = ctk.CTkFrame(self.students_frame, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True)
            
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="",
                font=("Arial", 40),
                text_color="#bdc3c7"
            )
            empty_icon.pack(pady=(50, 10))
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="No students found",
                font=("Arial", 16, "bold"),
                text_color="#7f8c8d"
            )
            empty_label.pack()
            
            empty_sub = ctk.CTkLabel(
                empty_frame,
                text="Click '+ Add Student' to create a new student record",
                font=("Arial", 12),
                text_color="#95a5a6"
            )
            empty_sub.pack(pady=(5, 0))
            
            return
        
        # ===== TABLE HEADER =====
        self.col_widths = [
            40,    # #
            110,   # Student ID
            170,   # Student Name
            120,   # Family ID
            90,    # Class
            70,    # Section
            100,   # Monthly Fee
            100,   # Concession
            80,    # Status
            190    # Actions
        ]
        
        self.headers = [
            "#", "Student ID", "Student Name", "Family ID", 
            "Class", "Section", "Monthly Fee", "Concession", 
            "Status", "Actions"
        ]
        
        # Header row
        header_row = ctk.CTkFrame(
            self.students_frame,
            fg_color="#1e3a5f",
            height=40,
            corner_radius=0
        )
        header_row.pack(fill="x")
        header_row.pack_propagate(False)
        
        for i, (header_text, width) in enumerate(zip(self.headers, self.col_widths)):
            cell_frame = ctk.CTkFrame(
                header_row,
                fg_color="#1e3a5f",
                width=width,
                height=40,
                corner_radius=0
            )
            cell_frame.pack(side="left", padx=0, pady=0)
            cell_frame.pack_propagate(False)
            
            align = "center" if i in [0, 5, 8, 9] else "w"
            if i in [6, 7]:
                align = "e"
            
            header_label = ctk.CTkLabel(
                cell_frame,
                text=header_text,
                font=("Arial", 11, "bold"),
                text_color="white",
                anchor=align,
                padx=8
            )
            header_label.pack(fill="both", expand=True)
        
        separator = ctk.CTkFrame(self.students_frame, fg_color="#e0e0e0", height=1)
        separator.pack(fill="x")
        
        # ===== TABLE BODY (NO SCROLLBAR) =====
        self.table_body = ctk.CTkFrame(
            self.students_frame,
            fg_color="white",
            corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)
        
        for idx, student in enumerate(students):
            self.create_student_row(student, idx)
    
    def create_student_row(self, student, idx):
        """Create a single student row - Spreadsheet Style"""
        
        guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
        family_id = guardian.family_id if guardian else "N/A"
        
        row_bg = "#ffffff" if idx % 2 == 0 else "#f8f9fa"
        
        row_frame = ctk.CTkFrame(
            self.table_body,
            fg_color=row_bg,
            height=50
        )
        row_frame.pack(fill="x", pady=0)
        row_frame.pack_propagate(False)
        
        row_values = [
            str(idx + 1),
            student.student_id,
            f"{student.first_name} {student.last_name}",
            family_id,
            student.class_grade,
            student.section or "-",
            f"Rs. {student.monthly_tuition_fee:,.0f}",
            f"Rs. {student.fee_concession:,.0f}",
            "Active" if student.academic_status.value == "active" else "Inactive"
        ]
        
        for i, (value, width) in enumerate(zip(row_values, self.col_widths)):
            cell_frame = ctk.CTkFrame(
                row_frame,
                fg_color=row_bg,
                width=width,
                height=50,
                corner_radius=0
            )
            cell_frame.pack(side="left", padx=0, pady=0)
            cell_frame.pack_propagate(False)
            
            align = "center" if i in [0, 5, 8] else "w"
            if i in [6, 7]:
                align = "e"
            
            text_color = "#2c3e50"
            font_weight = "normal"
            
            if i == 1:
                text_color = "#3498db"
                font_weight = "bold"
            elif i == 2:
                font_weight = "bold"
            elif i == 6:
                text_color = "#27ae60"
                font_weight = "bold"
            elif i == 7:
                text_color = "#8e44ad"
                font_weight = "bold"
            elif i == 8:
                if value == "Active":
                    text_color = "#27ae60"
                else:
                    text_color = "#e74c3c"
                font_weight = "bold"
            
            cell_label = ctk.CTkLabel(
                cell_frame,
                text=value,
                font=("Arial", 11, font_weight),
                text_color=text_color,
                anchor=align,
                justify="left" if align == "w" else "center",
                wraplength=width - 10,
                padx=8
            )
            cell_label.pack(fill="both", expand=True, padx=2, pady=2)
        
        # ===== ACTIONS COLUMN =====
        action_frame = ctk.CTkFrame(
            row_frame,
            fg_color=row_bg,
            width=self.col_widths[9],
            height=50,
            corner_radius=0
        )
        action_frame.pack(side="left", padx=0, pady=0)
        action_frame.pack_propagate(False)
        
        view_btn = ctk.CTkButton(
            action_frame,
            text="View",
            width=45,
            height=26,
            font=("Arial", 10, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            corner_radius=4,
            command=lambda sid=student.id: self.view_student(sid)
        )
        view_btn.pack(side="left", padx=(5, 2), pady=12)
        
        edit_btn = ctk.CTkButton(
            action_frame,
            text="Edit",
            width=45,
            height=26,
            font=("Arial", 10, "bold"),
            fg_color="#f39c12",
            hover_color="#e67e22",
            corner_radius=4,
            command=lambda sid=student.id: self.edit_student(sid)
        )
        edit_btn.pack(side="left", padx=2, pady=12)
        
        delete_btn = ctk.CTkButton(
            action_frame,
            text="Del",
            width=40,
            height=26,
            font=("Arial", 10, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            corner_radius=4,
            command=lambda sid=student.id: self.delete_student(sid)
        )
        delete_btn.pack(side="left", padx=2, pady=12)
    
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
    
    def search_students(self):
        """Search for students"""
        search_term = self.search_entry.get().strip()
        if search_term:
            results = self.student_service.search_students(search_term)
            self.refresh_students_list(results)
        else:
            self.refresh_students_list()
    
    def clear_search(self):
        """Clear search and show all students"""
        self.search_entry.delete(0, "end")
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
                f"Section: {student.section}\n"
                f"Monthly Fee: Rs. {student.monthly_tuition_fee:,.0f}\n"
                f"Concession: Rs. {student.fee_concession:,.0f}\n"
                f"Status: {student.academic_status.value}")
    
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