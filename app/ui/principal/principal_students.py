"""
Principal Students View - View Only
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.database.models import SessionLocal, Student, Guardian

class PrincipalStudentsView(ctk.CTkFrame):
    """Principal Students View - Read Only"""
    
    def __init__(self, parent, db=None):
        super().__init__(parent)
        
        self.db = db if db else SessionLocal()
        
        # Create UI
        self.create_widgets()
        self.refresh_students_list()
    
    def create_widgets(self):
        """Create main UI widgets"""
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=100)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Student Management (View Only)",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        # Students list frame
        self.students_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.students_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
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
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.students_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Student cards
        for student in students:
            student_card = ctk.CTkFrame(scroll_frame, fg_color="#f8f9fa", corner_radius=8)
            student_card.pack(fill="x", padx=10, pady=5)
            
            guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
            family_id = guardian.family_id if guardian else "N/A"
            
            info_text = f"{student.full_name} | ID: {student.student_id} | Family: {family_id} | Class: {student.class_grade} | Fee: Rs. {student.monthly_tuition_fee:,.0f}"
            
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
        from app.ui.student_details_screen import StudentDetailsWindow
        StudentDetailsWindow(self, student_id, self.db)
