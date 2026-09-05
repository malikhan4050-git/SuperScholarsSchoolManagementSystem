"""
Student Promotion Screen for Super Scholars School Management System
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal, Student, Guardian
from app.services.student_service import StudentService

class PromotionScreen(ctk.CTkFrame):
    """Student Promotion Screen - Select students from a class and promote them"""
    
    def __init__(self, parent, db=None, student_service=None):
        super().__init__(parent)
        
        # Database
        self.db = db if db else SessionLocal()
        self.student_service = student_service or StudentService(self.db)
        
        # Store data
        self.class_students = []
        self.selected_students = []
        self.student_checkboxes = []
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create main UI widgets"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        self.create_header()
        
        # Search and Controls Frame
        self.create_search_controls()
        
        # Students Display Area
        self.create_students_area()
        
        # Buttons Frame
        self.create_buttons()
    
    def create_header(self):
        """Create header section"""
        
        header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=70)
        header_frame.pack(fill="x", padx=20, pady=(15, 8))
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Student Promotion",
            font=("Arial", 22, "bold"),
            text_color="#1e3a5f"
        )
        title.pack(side="left", padx=20, pady=18)
    
    def create_search_controls(self):
        """Create search and control widgets - More compact"""
        
        control_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=8)
        control_frame.pack(fill="x", padx=20, pady=8)
        
        # ===== CLASS SEARCH =====
        class_label = ctk.CTkLabel(
            control_frame,
            text="Class:",
            font=("Arial", 13, "bold"),
            text_color="#1e3a5f"
        )
        class_label.pack(side="left", padx=(15, 5), pady=12)
        
        self.class_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="Enter class (e.g., 5, 10)",
            font=("Arial", 12),
            height=35,
            width=180,
            border_color="#bdc3c7",
            fg_color="#f8f9fa",
            corner_radius=6
        )
        self.class_entry.pack(side="left", padx=5, pady=12)
        self.class_entry.bind("<Return>", lambda e: self.search_class())
        
        self.search_btn = ctk.CTkButton(
            control_frame,
            text="Load Students",
            font=("Arial", 11, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            width=110,
            height=35,
            corner_radius=6,
            command=self.search_class
        )
        self.search_btn.pack(side="left", padx=5, pady=12)
        
        self.clear_btn = ctk.CTkButton(
            control_frame,
            text="Reset",
            font=("Arial", 11, "bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            width=65,
            height=35,
            corner_radius=6,
            command=self.clear_search
        )
        self.clear_btn.pack(side="left", padx=5, pady=12)
        
        # ===== SELECT ALL CHECKBOX =====
        self.check_all_var = ctk.BooleanVar(value=False)
        self.check_all_checkbox = ctk.CTkCheckBox(
            control_frame,
            text="Select All",
            variable=self.check_all_var,
            command=self.toggle_check_all,
            font=("Arial", 12, "bold"),
            text_color="#1e3a5f"
        )
        self.check_all_checkbox.pack(side="right", padx=15, pady=12)
    
    def create_students_area(self):
        """Create the students display area - Cards in a grid"""
        
        # Main container
        self.students_area = ctk.CTkFrame(self, fg_color="white", corner_radius=8)
        self.students_area.pack(fill="both", expand=True, padx=20, pady=8)
        
        # Placeholder message
        self.empty_frame = ctk.CTkFrame(self.students_area, fg_color="transparent")
        self.empty_frame.pack(fill="both", expand=True)
        
        self.empty_label = ctk.CTkLabel(
            self.empty_frame,
            text="Enter a class number and click 'Load Students'",
            font=("Arial", 16, "bold"),
            text_color="#7f8c8d"
        )
        self.empty_label.pack(pady=40)
        
        self.empty_sub = ctk.CTkLabel(
            self.empty_frame,
            text="Students will appear here for selection",
            font=("Arial", 13),
            text_color="#95a5a6"
        )
        self.empty_sub.pack(pady=(5, 0))
    
    def create_buttons(self):
        """Create action buttons"""
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        self.promote_btn = ctk.CTkButton(
            button_frame,
            text="Promote Selected Students",
            font=("Arial", 13, "bold"),
            fg_color="#27ae60",
            hover_color="#229954",
            width=220,
            height=45,
            corner_radius=8,
            command=self.promote_selected
        )
        self.promote_btn.pack(side="left", padx=10)
        self.promote_btn.configure(state="disabled")
        
        self.refresh_btn = ctk.CTkButton(
            button_frame,
            text="Clear",
            font=("Arial", 13, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            width=100,
            height=45,
            corner_radius=8,
            command=self.clear_search
        )
        self.refresh_btn.pack(side="left", padx=10)
    
    def search_class(self):
        """Search for students in the entered class"""
        
        class_input = self.class_entry.get().strip()
        
        if not class_input:
            messagebox.showwarning("Warning", "Please enter a class number!")
            return
        
        import re
        class_num = ''.join(re.findall(r'\d+', class_input))
        
        if not class_num:
            messagebox.showwarning("Warning", "Please enter a valid class number!")
            return
        
        class_name = f"Class {class_num}" if not class_input.startswith("Class") else class_input
        
        self.class_students = self.student_service.get_students_by_class(class_name)
        
        if not self.class_students:
            messagebox.showinfo("No Students", f"No students found in {class_name}!")
            self.clear_students_area()
            return
        
        self.display_students()
        self.promote_btn.configure(state="normal")
    
    def display_students(self):
        """Display students as professional cards in a grid"""
        
        # Clear existing content
        self.clear_students_area()
        
        # Header showing class info
        class_name = self.class_students[0].class_grade if self.class_students else "Unknown"
        
        # Create a header bar
        info_bar = ctk.CTkFrame(
            self.students_area,
            fg_color="#1e3a5f",
            height=50,
            corner_radius=8
        )
        info_bar.pack(fill="x", padx=10, pady=10)
        info_bar.pack_propagate(False)
        
        info_text = f"Students in {class_name} ({len(self.class_students)} students found)"
        info_label = ctk.CTkLabel(
            info_bar,
            text=info_text,
            font=("Arial", 14, "bold"),
            text_color="white"
        )
        info_label.pack(side="left", padx=15, pady=12)
        
        # Scrollable frame for cards
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.students_area,
            fg_color="white",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Store references
        self.student_checkboxes = []
        self.selected_students = []
        
        # Display each student as a card
        for idx, student in enumerate(self.class_students):
            self.create_student_card(student, idx)
        
        # Update Select All checkbox
        self.check_all_var.set(True)
    
    def create_student_card(self, student, idx):
        """Create a single student card"""
        
        guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
        family_id = guardian.family_id if guardian else "N/A"
        
        # Create card frame
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#f8f9fa" if idx % 2 == 0 else "white",
            corner_radius=8,
            border_width=1,
            border_color="#e0e0e0"
        )
        card.pack(fill="x", padx=5, pady=5)
        
        # Left side: Checkbox and Student Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        
        # Checkbox
        check_var = ctk.BooleanVar(value=True)
        checkbox = ctk.CTkCheckBox(
            info_frame,
            text="",
            variable=check_var,
            width=25,
            command=lambda sid=student.id, cv=check_var: self.toggle_student(sid, cv)
        )
        checkbox.pack(side="left", padx=(0, 10))
        
        # Student Name (Bold)
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"{student.first_name} {student.last_name}",
            font=("Arial", 13, "bold"),
            text_color="#2c3e50",
            anchor="w"
        )
        name_label.pack(side="left", padx=(0, 15))
        
        # Student ID (Blue)
        id_label = ctk.CTkLabel(
            info_frame,
            text=f"ID: {student.student_id}",
            font=("Arial", 12, "bold"),
            text_color="#3498db",
            anchor="w"
        )
        id_label.pack(side="left", padx=(0, 15))
        
        # Family ID
        fam_label = ctk.CTkLabel(
            info_frame,
            text=f"Family: {family_id}",
            font=("Arial", 11),
            text_color="#7f8c8d",
            anchor="w"
        )
        fam_label.pack(side="left", padx=(0, 15))
        
        # Monthly Fee (Green)
        fee_label = ctk.CTkLabel(
            info_frame,
            text=f"Rs. {student.monthly_tuition_fee:,.0f}",
            font=("Arial", 12, "bold"),
            text_color="#27ae60",
            anchor="w"
        )
        fee_label.pack(side="left", padx=(0, 15))
        
        # Right side: Status and View Button
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(side="right", padx=10, pady=8)
        
        # Status
        status_text = "Active" if student.academic_status.value == "active" else "Inactive"
        status_color = "#27ae60" if status_text == "Active" else "#e74c3c"
        
        status_label = ctk.CTkLabel(
            action_frame,
            text=status_text,
            font=("Arial", 11, "bold"),
            text_color=status_color
        )
        status_label.pack(side="left", padx=(0, 10))
        
        # View Button (Small)
        view_btn = ctk.CTkButton(
            action_frame,
            text="View",
            width=50,
            height=28,
            font=("Arial", 10, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            corner_radius=4,
            command=lambda sid=student.id: self.view_student(sid)
        )
        view_btn.pack(side="left")
        
        # Store references
        self.student_checkboxes.append((student, check_var))
        self.selected_students.append(student.id)
    
    def clear_students_area(self):
        """Clear the students area"""
        for widget in self.students_area.winfo_children():
            widget.destroy()
        
        self.class_students = []
        self.selected_students = []
        self.student_checkboxes = []
        self.promote_btn.configure(state="disabled")
    
    def toggle_student(self, student_id, check_var):
        """Toggle student selection"""
        if check_var.get():
            if student_id not in self.selected_students:
                self.selected_students.append(student_id)
        else:
            if student_id in self.selected_students:
                self.selected_students.remove(student_id)
        
        self.update_check_all_state()
    
    def toggle_check_all(self):
        """Toggle all students selection"""
        checked = self.check_all_var.get()
        self.selected_students = []
        
        for student, check_var in self.student_checkboxes:
            check_var.set(checked)
            
            if checked:
                self.selected_students.append(student.id)
    
    def update_check_all_state(self):
        """Update the Select All checkbox state"""
        total_students = len(self.student_checkboxes)
        selected_count = len(self.selected_students)
        
        if selected_count == 0:
            self.check_all_var.set(False)
        elif selected_count == total_students:
            self.check_all_var.set(True)
    
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
    
    def promote_selected(self):
        """Promote selected students to the next class"""
        
        if not self.selected_students:
            messagebox.showwarning("Warning", "Please select at least one student to promote!")
            return
        
        if not self.class_students:
            return
        
        current_class = self.class_students[0].class_grade
        
        next_class = self.student_service.get_next_class(current_class)
        
        confirm_msg = (
            f"Are you sure you want to promote {len(self.selected_students)} student(s)?\n\n"
            f"Current Class: {current_class}\n"
            f"Next Class: {next_class}\n\n"
            f"Their monthly fee will be updated based on the new class."
        )
        
        if messagebox.askyesno("Confirm Promotion", confirm_msg):
            result = self.student_service.promote_students(self.selected_students, current_class)
            
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.clear_search()
            else:
                messagebox.showerror("Error", result["message"])
    
    def clear_search(self):
        """Clear the search and reset the screen"""
        self.class_entry.delete(0, "end")
        self.check_all_var.set(False)
        self.clear_students_area()
        
        # Show placeholder message
        self.empty_frame = ctk.CTkFrame(self.students_area, fg_color="transparent")
        self.empty_frame.pack(fill="both", expand=True)
        
        self.empty_label = ctk.CTkLabel(
            self.empty_frame,
            text="Enter a class number and click 'Load Students'",
            font=("Arial", 16, "bold"),
            text_color="#7f8c8d"
        )
        self.empty_label.pack(pady=40)
        
        self.empty_sub = ctk.CTkLabel(
            self.empty_frame,
            text="Students will appear here for selection",
            font=("Arial", 13),
            text_color="#95a5a6"
        )
        self.empty_sub.pack(pady=(5, 0))