"""
Student Registration Form for Super Scholars School Management System
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from datetime import datetime, date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal, Student, Guardian
from app.services.student_service import StudentService
from app.utils.center_window import center_window, center_and_maximize  # UI FIX

class StudentRegistrationForm(ctk.CTkToplevel):
    """Professional Student Registration Form - Supports Add & Edit Modes"""
    
    def __init__(self, parent, student_service=None, student=None):
        super().__init__(parent)
        
        # Configure window
        self.title("Student Registration - Super Scholars")
        self.geometry("1000x800")
        self.resizable(True, True)
        
        # Set theme
        ctk.set_appearance_mode("light")
        
        # Store services
        self.student_service = student_service or StudentService(SessionLocal())
        
        # Store the student being edited (None for add mode)
        self.editing_student = student
        self.is_edit_mode = student is not None
        
        # Store form entries
        self.form_entries = {}
        
        # UI FIX: Center and maximize window after creation
        self.after(100, lambda: center_and_maximize(self))
        
        # Create UI
        self.create_widgets()
        
        # If editing, pre-fill the form
        if self.is_edit_mode:
            self.pre_fill_form()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create the form widgets"""
        
        # Main container with padding
        self.main_container = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=15
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Scrollable form area
        self.form_scroll = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="white",
            corner_radius=10
        )
        self.form_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create form sections
        self.create_personal_info_section()
        self.create_guardian_info_section()
        self.create_academic_info_section()
        self.create_fee_info_section()
        
        # Footer with buttons
        self.create_footer()
    
    def create_header(self):
        """Create form header"""
        
        header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#1e3a5f",
            corner_radius=10,
            height=80
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)  # UI FIX: keep height consistent
        
        # Title - Change based on mode
        title_text = "Edit Student" if self.is_edit_mode else "Student Registration Form"
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Fill in all required fields marked with *",
            font=("Arial", 13),
            text_color="#a0b4c8"
        )
        subtitle_label.pack(pady=(0, 15))
    
    def create_section_header(self, parent, title):
        """Create a section header"""
        
        # Section header frame
        section_frame = ctk.CTkFrame(
            parent,
            fg_color="#f0f2f5",
            corner_radius=10,
            height=50
        )
        section_frame.pack(fill="x", padx=10, pady=(15, 10))
        section_frame.pack_propagate(False)  # UI FIX: keep height consistent
        
        # Section title
        section_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        section_label.pack(side="left", padx=20, pady=10)
    
    def create_input_row(self, parent, label_text, field_name, row, column=0, required=False):
        """Create a labeled input row in grid layout"""
        
        # Create frame for the input
        input_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        input_frame.grid(row=row, column=column, padx=10, pady=8, sticky="ew")
        
        # Configure grid columns
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=2)
        
        # Label
        label_text_display = f"{label_text} *" if required else label_text
        label = ctk.CTkLabel(
            input_frame,
            text=label_text_display,
            font=("Arial", 13, "bold" if required else "normal"),
            text_color="#2c3e50" if not required else "#e74c3c",
            anchor="w"
        )
        label.grid(row=0, column=0, padx=(10, 5), sticky="w")
        
        # Entry
        entry = ctk.CTkEntry(
            input_frame,
            height=38,
            font=("Arial", 13),
            border_color="#bdc3c7",
            fg_color="#f8f9fa",
            placeholder_text=f"Enter {label_text.lower()}..."
        )
        entry.grid(row=0, column=1, padx=(5, 10), sticky="ew")
        
        # Store entry
        self.form_entries[field_name] = entry
        
        return entry
    
    def create_personal_info_section(self):
        """Create personal information section"""
        
        self.create_section_header(self.form_scroll, "Personal Information")
        
        # Create grid frame for inputs
        grid_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=10)
        
        # Configure grid columns
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        # Row 1 - First Name and Last Name
        self.create_input_row(grid_frame, "First Name", "first_name", 0, 0, required=True)
        self.create_input_row(grid_frame, "Last Name", "last_name", 0, 1, required=True)
        
        # Row 2 - DOB and Gender
        self.create_input_row(grid_frame, "Date of Birth", "dob", 1, 0, required=True)
        self.create_input_row(grid_frame, "Gender", "gender", 1, 1, required=True)
        
        # Row 3 - CNIC/B-Form
        self.create_input_row(grid_frame, "CNIC/B-Form", "cnic", 2, 0)
    
    def create_guardian_info_section(self):
        """Create guardian information section"""
        
        self.create_section_header(self.form_scroll, "Guardian Information")
        
        # Create grid frame for inputs
        grid_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=10)
        
        # Configure grid columns
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        # Row 1 - Guardian Name and CNIC
        self.create_input_row(grid_frame, "Guardian Name", "guardian_name", 0, 0, required=True)
        self.create_input_row(grid_frame, "Guardian CNIC", "guardian_cnic", 0, 1, required=True)
        
        # Row 2 - Guardian contact details
        self.create_input_row(grid_frame, "Mobile Number", "mobile", 1, 0, required=True)
        self.create_input_row(grid_frame, "Email", "email", 1, 1)

        # Row 3 - Guardian addresses
        self.create_input_row(grid_frame, "Current Address", "current_address", 2, 0)
        self.create_input_row(grid_frame, "Permanent Address", "permanent_address", 2, 1)

        # Row 4 - Occupation and Income
        self.create_input_row(grid_frame, "Guardian Occupation", "guardian_occupation", 3, 0)
        self.create_input_row(grid_frame, "Monthly Income", "guardian_income", 3, 1)

        # Row 5 - Emergency Contact Name and Number
        self.create_input_row(grid_frame, "Emergency Name", "emergency_name", 4, 0)
        self.create_input_row(grid_frame, "Emergency Phone", "emergency_phone", 4, 1)
    
    def create_academic_info_section(self):
        """Create academic information section"""
        
        self.create_section_header(self.form_scroll, "Academic Information")
        
        # Create grid frame for inputs
        grid_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=10)
        
        # Configure grid columns
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        # Row 1 - Admission Date and Class
        self.create_input_row(grid_frame, "Admission Date", "admission_date", 0, 0, required=True)
        self.create_input_row(grid_frame, "Class/Grade", "class_grade", 0, 1, required=True)
        
        # Row 2 - Section
        self.create_input_row(grid_frame, "Section", "section", 1, 0)
    
    def create_fee_info_section(self):
        """Create fee information section - Monthly Fee + Fee Concession"""
        
        self.create_section_header(self.form_scroll, "Fee Information")
        
        # Create grid frame for inputs
        grid_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=10)
        
        # Configure grid columns
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        # Row 1 - Monthly Fee
        self.create_input_row(grid_frame, "Monthly Fee", "monthly_fee", 0, 0, required=True)
        
        # Row 2 - Fee Concession
        self.create_input_row(grid_frame, "Fee Concession", "fee_concession", 1, 0)
    
    def create_footer(self):
        """Create footer with action buttons"""
        
        footer_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="white",
            corner_radius=10
        )
        footer_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Cancel Button
        cancel_btn = ctk.CTkButton(
            footer_frame,
            text="Cancel",
            width=120,
            height=45,
            font=("Arial", 15, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.destroy
        )
        cancel_btn.pack(side="right", padx=10, pady=10)
        
        # Clear Button
        clear_btn = ctk.CTkButton(
            footer_frame,
            text="Clear Form",
            width=120,
            height=45,
            font=("Arial", 15, "bold"),
            fg_color="#f39c12",
            hover_color="#e67e22",
            command=self.clear_form
        )
        clear_btn.pack(side="right", padx=10, pady=10)
        
        # Submit Button - Change text based on mode
        submit_text = "Update Student" if self.is_edit_mode else "Register Student"
        submit_btn = ctk.CTkButton(
            footer_frame,
            text=submit_text,
            width=200,
            height=45,
            font=("Arial", 15, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.submit_form
        )
        submit_btn.pack(side="right", padx=10, pady=10)
    
    def pre_fill_form(self):
        """Pre-fill the form fields when editing a student"""
        if not self.editing_student:
            return
        
        # Get the student data
        student = self.editing_student
        
        # Get guardian data
        guardian = None
        if student.guardian_id:
            guardian = self.student_service.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
        
        # Pre-fill personal information
        self.form_entries['first_name'].insert(0, student.first_name)
        self.form_entries['last_name'].insert(0, student.last_name)
        self.form_entries['dob'].insert(0, student.date_of_birth.strftime("%Y-%m-%d"))
        self.form_entries['gender'].insert(0, student.gender.value)
        self.form_entries['cnic'].insert(0, student.cnic_bform or "")
        
        # Pre-fill guardian information
        if guardian:
            self.form_entries['guardian_name'].insert(0, guardian.guardian_name)
            self.form_entries['guardian_cnic'].insert(0, guardian.cnic or "")
            self.form_entries['mobile'].insert(0, guardian.mobile_number)
            self.form_entries['email'].insert(0, guardian.email or "")
            self.form_entries['current_address'].insert(0, guardian.address or "")
            self.form_entries['permanent_address'].insert(0, guardian.permanent_address or "")
            self.form_entries['guardian_occupation'].insert(0, guardian.occupation or "")
            self.form_entries['guardian_income'].insert(0, str(guardian.monthly_income or 0))
            self.form_entries['emergency_name'].insert(0, guardian.emergency_contact_name or "")
            self.form_entries['emergency_phone'].insert(0, guardian.emergency_contact_number or "")
        
        # Pre-fill academic information
        self.form_entries['admission_date'].insert(0, student.admission_date.strftime("%Y-%m-%d"))
        self.form_entries['class_grade'].insert(0, student.class_grade)
        self.form_entries['section'].insert(0, student.section or "")
        
        # Pre-fill fee information
        self.form_entries['monthly_fee'].insert(0, str(student.monthly_tuition_fee))
        self.form_entries['fee_concession'].insert(0, str(student.fee_concession or 0))
    
    def clear_form(self):
        """Clear all form fields"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all fields?"):
            for entry in self.form_entries.values():
                entry.delete(0, "end")
    
    def submit_form(self):
        """Submit the form - Create or Update student"""
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'dob', 'gender', 'guardian_name', 
                          'guardian_cnic', 'mobile', 'admission_date', 
                          'class_grade', 'monthly_fee']
        
        for field in required_fields:
            if field not in self.form_entries or not self.form_entries[field].get().strip():
                messagebox.showwarning("Warning", f"Please fill all required fields!")
                return
        
        # Gather data
        student_data = {}
        for field, entry in self.form_entries.items():
            student_data[field] = entry.get().strip()
        
        if self.is_edit_mode:
            # Update existing student
            result = self.student_service.update_student(self.editing_student.id, student_data)
            if result["success"]:
                messagebox.showinfo("Success", "Student updated successfully!")
                self.destroy()
            else:
                messagebox.showerror("Error", result["message"])
        else:
            # Create new student
            result = self.student_service.create_student(student_data)
            if result["success"]:
                messagebox.showinfo("Success", 
                    f"Student created successfully!\n\n"
                    f"Student ID: {result['student_id']}\n"
                    f"Family ID: {result['family_id']}")
                self.destroy()
            else:
                messagebox.showerror("Error", result["message"])
    
    def on_close(self):
        """Handle window close"""
        self.destroy()