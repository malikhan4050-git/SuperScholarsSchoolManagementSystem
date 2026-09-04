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
        
        # Students List Frame
        self.create_students_list()
        
        # Buttons Frame
        self.create_buttons()
    
    def create_header(self):
        """Create header section"""
        
        header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Student Promotion",
            font=("Arial", 28, "bold"),
            text_color="#1e3a5f"
        )
        title.pack(side="left", padx=10, pady=20)
    
    def create_search_controls(self):
        """Create search and control widgets"""
        
        control_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # ===== CLASS SEARCH =====
        class_label = ctk.CTkLabel(
            control_frame,
            text="Enter Class:",
            font=("Arial", 14, "bold"),
            text_color="#1e3a5f"
        )
        class_label.pack(side="left", padx=(20, 10), pady=15)
        
        self.class_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="e.g., 5, 10, Class 10...",
            font=("Arial", 13),
            height=40,
            width=200,
            border_color="#bdc3c7",
            fg_color="#f8f9fa"
        )
        self.class_entry.pack(side="left", padx=10, pady=15)
        self.class_entry.bind("<Return>", lambda e: self.search_class())
        
        self.search_btn = ctk.CTkButton(
            control_frame,
            text="Search",
            font=("Arial", 12, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            width=100,
            height=40,
            command=self.search_class
        )
        self.search_btn.pack(side="left", padx=5, pady=15)
        
        self.clear_btn = ctk.CTkButton(
            control_frame,
            text="Clear",
            font=("Arial", 12, "bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            width=80,
            height=40,
            command=self.clear_search
        )
        self.clear_btn.pack(side="left", padx=5, pady=15)
        
        # ===== SELECT ALL CHECKBOX =====
        self.check_all_var = ctk.BooleanVar(value=False)
        self.check_all_checkbox = ctk.CTkCheckBox(
            control_frame,
            text="Select All",
            variable=self.check_all_var,
            command=self.toggle_check_all,
            font=("Arial", 13, "bold"),
            text_color="#1e3a5f"
        )
        self.check_all_checkbox.pack(side="right", padx=20, pady=15)
    
    def create_students_list(self):
        """Create the scrollable students list"""
        
        # Main container
        self.students_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.students_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollable area
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.students_frame,
            fg_color="white",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Placeholder message
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Enter a class number and click Search to load students.",
            font=("Arial", 16),
            text_color="gray"
        )
        self.empty_label.pack(pady=50)
    
    def create_buttons(self):
        """Create action buttons"""
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        self.promote_btn = ctk.CTkButton(
            button_frame,
            text="Promote Selected Students",
            font=("Arial", 14, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=250,
            height=50,
            command=self.promote_selected
        )
        self.promote_btn.pack(side="left", padx=10)
        self.promote_btn.configure(state="disabled")  # Disabled until students are loaded
        
        self.refresh_btn = ctk.CTkButton(
            button_frame,
            text="Refresh",
            font=("Arial", 14, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            width=120,
            height=50,
            command=self.clear_search
        )
        self.refresh_btn.pack(side="left", padx=10)
    
    def search_class(self):
        """Search for students in the entered class"""
        
        # Get the class input
        class_input = self.class_entry.get().strip()
        
        if not class_input:
            messagebox.showwarning("Warning", "Please enter a class number!")
            return
        
        # Clean the input - extract only numbers
        import re
        class_num = ''.join(re.findall(r'\d+', class_input))
        
        if not class_num:
            messagebox.showwarning("Warning", "Please enter a valid class number!")
            return
        
        # Format the class name
        class_name = f"Class {class_num}" if not class_input.startswith("Class") else class_input
        
        # Get students from this class
        self.class_students = self.student_service.get_students_by_class(class_name)
        
        if not self.class_students:
            messagebox.showinfo("No Students", f"No students found in {class_name}!")
            self.clear_students_list()
            return
        
        # Display students
        self.display_students()
        
        # Enable promote button
        self.promote_btn.configure(state="normal")
    
    def display_students(self):
        """Display the students in the scrollable frame"""
        
        # Clear existing widgets
        self.clear_students_list()
        
        # Show header with class info
        if self.class_students:
            class_name = self.class_students[0].class_grade if self.class_students else "Unknown"
            header_label = ctk.CTkLabel(
                self.scroll_frame,
                text=f"Students in {class_name} ({len(self.class_students)} students)",
                font=("Arial", 18, "bold"),
                text_color="#1e3a5f"
            )
            header_label.pack(pady=(0, 10))
        
        # Display each student with a checkbox
        self.student_checkboxes = []
        self.selected_students = []
        
        for student in self.class_students:
            # Create a card for each student
            student_card = ctk.CTkFrame(
                self.scroll_frame,
                fg_color="#f8f9fa",
                corner_radius=8
            )
            student_card.pack(fill="x", padx=10, pady=5)
            
            # Get guardian info
            guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
            family_id = guardian.family_id if guardian else "N/A"
            
            # Student info
            info_text = f"{student.full_name} | ID: {student.student_id} | Family: {family_id} | Fee: Rs. {student.monthly_tuition_fee:,.0f}"
            
            # Checkbox
            check_var = ctk.BooleanVar(value=True)  # Default to selected
            checkbox = ctk.CTkCheckBox(
                student_card,
                text=info_text,
                variable=check_var,
                font=("Arial", 13),
                text_color="#2c3e50",
                command=lambda sid=student.id, cv=check_var: self.toggle_student(sid, cv)
            )
            checkbox.pack(side="left", padx=15, pady=10)
            
            # Store references
            self.student_checkboxes.append((student, check_var))
            
            # Initially select all
            self.selected_students.append(student.id)
        
        # Update select all checkbox
        self.check_all_var.set(True)
    
    def clear_students_list(self):
        """Clear the students list"""
        for widget in self.scroll_frame.winfo_children():
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
    
    def promote_selected(self):
        """Promote selected students to the next class"""
        
        if not self.selected_students:
            messagebox.showwarning("Warning", "Please select at least one student to promote!")
            return
        
        # Get current class
        if not self.class_students:
            return
        
        current_class = self.class_students[0].class_grade
        
        # Get next class name
        next_class = self.student_service.get_next_class(current_class)
        
        # Confirm promotion
        confirm_msg = (
            f"Are you sure you want to promote {len(self.selected_students)} student(s)?\n\n"
            f"Current Class: {current_class}\n"
            f"Next Class: {next_class}\n\n"
            f"Their monthly fee will be updated based on the new class."
        )
        
        if messagebox.askyesno("Confirm Promotion", confirm_msg):
            # Promote students
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
        self.clear_students_list()
        
        # Show placeholder message
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Enter a class number and click Search to load students.",
            font=("Arial", 16),
            text_color="gray"
        )
        self.empty_label.pack(pady=50)