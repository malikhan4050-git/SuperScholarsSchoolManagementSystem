"""
Super Admin Dashboard for Super Scholars School Management System
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal, User, UserRole, Guardian, Student
from app.utils.auth import Authentication
from app.services.fee_service import FeeService
from app.ui.fee_challan_screen import FeeChallanlScreen
from app.utils.center_window import center_and_maximize  # UI FIX

class SuperAdminDashboard(ctk.CTk):
    """Super Admin Dashboard Class"""
    
    def __init__(self, user):
        super().__init__()
        
        # Store current user
        self.current_user = user
        
        # Configure window
        self.title("Super Scholars - Super Admin Dashboard")
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # UI FIX: Center and maximize window after creation
        self.after(100, lambda: center_and_maximize(self))
        
        # Initialize database
        self.db = SessionLocal()
        self.auth = Authentication(self.db)
        self.auth.current_user = user
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
        self.sidebar.grid_propagate(False)  # UI FIX: Keep fixed width
        
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
            text="Super Admin",
            font=("Arial", 12),
            text_color="#a0b4c8"
        )
        self.user_role.pack(pady=(0, 10))
        
        # Navigation buttons
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Manage Users", self.show_users),
            ("Manage Students", self.show_students),
            ("Fee Management", self.show_fees),
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
            height=100,
            fg_color="white",
            corner_radius=0
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)  # UI FIX: keep height consistent
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Dashboard Overview",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        # Stats cards
        self.stats_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        self.stats_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Get actual stats
        total_users = self.db.query(User).count()
        total_admins = self.db.query(User).filter(User.role == UserRole.ADMIN).count()
        total_principals = self.db.query(User).filter(User.role == UserRole.PRINCIPAL).count()
        total_students = self.db.query(Student).count()
        total_families = self.db.query(Guardian).count()
        
        stats = [
            ("Total Users", total_users, "#3498db"),
            ("Admins", total_admins, "#2ecc71"),
            ("Principals", total_principals, "#e74c3c"),
            ("Students", total_students, "#f39c12"),
            ("Families", total_families, "#9b59b6")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = ctk.CTkFrame(
                self.stats_frame,
                width=200,
                height=150,
                fg_color="white",
                corner_radius=15
            )
            card.grid(row=0, column=i, padx=10, pady=10)
            
            value_label = ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 36, "bold"),
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
    
    def show_users(self):
        """Show user management view"""
        self.clear_main_content()
        
        # Header
        self.header_frame = ctk.CTkFrame(
            self.main_content,
            height=100,
            fg_color="white",
            corner_radius=0
        )
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)  # UI FIX
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="User Management",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        # Add User Button
        self.add_user_btn = ctk.CTkButton(
            self.header_frame,
            text="+ Add User",
            width=150,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.show_add_user_form
        )
        self.add_user_btn.pack(side="right", padx=30, pady=20)
        
        # Users list frame
        self.users_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=10
        )
        self.users_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Refresh users list
        self.refresh_users_list()
    
    def refresh_users_list(self):
        """Refresh the users list"""
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        # Title
        list_title = ctk.CTkLabel(
            self.users_frame,
            text="All Users",
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        list_title.pack(pady=10)
        
        # Get all users
        users = self.db.query(User).all()
        
        # User cards
        for user in users:
            user_card = ctk.CTkFrame(
                self.users_frame,
                fg_color="#f8f9fa",
                corner_radius=8
            )
            user_card.pack(fill="x", padx=20, pady=5)
            
            # User info
            info_text = f"{user.full_name} | @{user.username} | {user.role.value} | {'Active' if user.is_active else 'Inactive'}"
            
            user_label = ctk.CTkLabel(
                user_card,
                text=info_text,
                font=("Arial", 13),
                text_color="#2c3e50"
            )
            user_label.pack(side="left", padx=15, pady=10)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                user_card,
                text="Delete",
                width=80,
                height=30,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                command=lambda uid=user.id: self.delete_user(uid)
            )
            delete_btn.pack(side="right", padx=15, pady=5)
    
    def show_add_user_form(self):
        """Show form to add new user"""
        
        # Create modal dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New User")
        dialog.geometry("500x650")
        dialog.grab_set()
        
        # UI FIX: Center dialog
        from app.utils.center_window import center_window
        dialog.after(100, lambda: center_window(dialog, 500, 650))
        
        # Form frame
        form_frame = ctk.CTkFrame(dialog, fg_color="white", corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            form_frame,
            text="Create New User",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        title.pack(pady=20)
        
        # Form fields
        fields = [
            ("Full Name", "entry_full_name"),
            ("Username", "entry_username"),
            ("Email", "entry_email"),
            ("Password", "entry_password")
        ]
        
        entries = {}
        
        for label_text, attr_name in fields:
            label = ctk.CTkLabel(
                form_frame,
                text=label_text,
                font=("Arial", 14, "bold"),
                text_color="#1e3a5f"
            )
            label.pack(anchor="w", padx=40, pady=(10, 5))
            
            entry = ctk.CTkEntry(
                form_frame,
                width=400,
                height=40,
                font=("Arial", 14)
            )
            entry.pack(padx=40, pady=(0, 10))
            
            entries[attr_name] = entry
        
        # Role selection
        role_label = ctk.CTkLabel(
            form_frame,
            text="Role",
            font=("Arial", 14, "bold"),
            text_color="#1e3a5f"
        )
        role_label.pack(anchor="w", padx=40, pady=(10, 5))
        
        role_var = ctk.StringVar(value="admin")
        role_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["admin", "principal"],
            variable=role_var,
            width=400,
            height=40,
            font=("Arial", 14)
        )
        role_menu.pack(padx=40, pady=(0, 20))
        
        # Create button
        create_btn = ctk.CTkButton(
            form_frame,
            text="Create User",
            width=200,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=lambda: self.create_user(entries, role_var, dialog)
        )
        create_btn.pack(pady=20)
    
    def create_user(self, entries, role_var, dialog):
        """Create a new user"""
        
        full_name = entries["entry_full_name"].get().strip()
        username = entries["entry_username"].get().strip()
        email = entries["entry_email"].get().strip()
        password = entries["entry_password"].get().strip()
        role = role_var.get()
        
        # Validate
        if not all([full_name, username, email, password]):
            messagebox.showwarning("Warning", "Please fill all fields!")
            return
        
        # Map role string to enum
        role_map = {
            "admin": UserRole.ADMIN,
            "principal": UserRole.PRINCIPAL
        }
        
        # Create user
        result = self.auth.create_user(
            username=username,
            password=password,
            email=email,
            full_name=full_name,
            role=role_map[role]
        )
        
        if result["success"]:
            messagebox.showinfo("Success", result["message"])
            dialog.destroy()
            self.refresh_users_list()
        else:
            messagebox.showerror("Error", result["message"])
    
    def delete_user(self, user_id):
        """Delete a user"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                self.db.delete(user)
                self.db.commit()
                messagebox.showinfo("Success", "User deleted successfully!")
                self.refresh_users_list()
    
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
        self.header_frame.pack_propagate(False)  # UI FIX
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Student Management",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        # Students list frame
        self.students_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=10
        )
        self.students_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Refresh students list
        self.refresh_students_list()
    
    def refresh_students_list(self):
        """Refresh the students list"""
        for widget in self.students_frame.winfo_children():
            widget.destroy()
        
        # Title
        list_title = ctk.CTkLabel(
            self.students_frame,
            text="All Students",
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        list_title.pack(pady=10)
        
        # Get all students
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
        
        # Create scrollable frame for students
        scroll_frame = ctk.CTkScrollableFrame(
            self.students_frame,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Student cards
        for student in students:
            student_card = ctk.CTkFrame(
                scroll_frame,
                fg_color="#f8f9fa",
                corner_radius=8
            )
            student_card.pack(fill="x", padx=10, pady=5)
            
            # Get guardian for this student
            guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
            family_id = guardian.family_id if guardian else "N/A"
            
            # Student info with family ID
            info_text = f"{student.full_name} | ID: {student.student_id} | Family: {family_id} | Class: {student.class_grade}"
            
            student_label = ctk.CTkLabel(
                student_card,
                text=info_text,
                font=("Arial", 13),
                text_color="#2c3e50"
            )
            student_label.pack(side="left", padx=15, pady=10)
            
            # View button
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
    
    def show_fees(self):
        """Show fee management view"""
        self.clear_main_content()
        
        # Create and display the Fee Challan Screen
        try:
            self.fee_challan_screen = FeeChallanlScreen(self.main_content, self.db)
            self.fee_challan_screen.pack(fill="both", expand=True)
        except Exception as e:
            # Fallback to placeholder if there's an error
            messagebox.showerror("Error", f"Failed to load Fee Challan screen: {str(e)}")
            
            # Header
            self.header_frame = ctk.CTkFrame(
                self.main_content,
                height=100,
                fg_color="white",
                corner_radius=0
            )
            self.header_frame.pack(fill="x")
            self.header_frame.pack_propagate(False)  # UI FIX
            
            self.header_title = ctk.CTkLabel(
                self.header_frame,
                text="Fee Management",
                font=("Arial", 24, "bold"),
                text_color="#1e3a5f"
            )
            self.header_title.pack(side="left", padx=30, pady=30)
            
            # Add placeholder content
            placeholder = ctk.CTkLabel(
                self.main_content,
                text="Fee Management features coming soon...",
                font=("Arial", 18),
                text_color="gray"
            )
            placeholder.pack(pady=100)
    
    def show_reports(self):
        """Show reports (placeholder)"""
        self.clear_main_content()
        
        header = ctk.CTkLabel(
            self.main_content,
            text="Reports (Coming Soon)",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        header.pack(pady=100)
    
    def show_settings(self):
        """Show settings (placeholder)"""
        self.clear_main_content()
        
        header = ctk.CTkLabel(
            self.main_content,
            text="Settings (Coming Soon)",
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
            
            # Import and show login window
            from app.ui.login_window import LoginWindow
            login_window = LoginWindow()
            login_window.mainloop()

if __name__ == "__main__":
    # Test with a dummy user
    from app.database.models import SessionLocal
    db = SessionLocal()
    user = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
    db.close()
    
    if user:
        app = SuperAdminDashboard(user)
        app.mainloop()