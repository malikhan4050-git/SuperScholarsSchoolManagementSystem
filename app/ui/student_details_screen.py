"""
Student Details Window - Full Screen View
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal, Student, Guardian, FeeRecord, FeeChallan
from app.services.student_service import StudentService
from app.services.fee_service import FeeService

class StudentDetailsWindow(ctk.CTkToplevel):
    """Full Screen Student Details Window"""
    
    def __init__(self, parent, student_id, db=None):
        super().__init__(parent)
        
        self.title("Student Details - Super Scholars")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        self.db = db if db else SessionLocal()
        self.student_service = StudentService(self.db)
        self.fee_service = FeeService(self.db)
        
        # Get student data
        self.student = self.student_service.get_student_by_id(student_id)
        if not self.student:
            messagebox.showerror("Error", "Student not found!")
            self.destroy()
            return
        
        # Get guardian
        self.guardian = self.db.query(Guardian).filter(Guardian.id == self.student.guardian_id).first()
        
        # Get fee records
        self.fee_records = self.db.query(FeeRecord).filter(FeeRecord.student_id == self.student.id).order_by(FeeRecord.due_date.desc()).all()
        
        # Get challans for this family
        self.challans = []
        if self.guardian:
            self.challans = self.db.query(FeeChallan).filter(FeeChallan.family_id == self.guardian.family_id).order_by(FeeChallan.challan_month.desc()).all()
        
        # Create UI
        self.create_widgets()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all widgets"""
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="#f0f2f5", corner_radius=0)
        main_frame.pack(fill="both", expand=True)
        
        # ===== HEADER =====
        header_frame = ctk.CTkFrame(main_frame, fg_color="#1e3a5f", corner_radius=0, height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Back button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Back",
            font=("Arial", 14, "bold"),
            fg_color="transparent",
            hover_color="#2c5282",
            width=80,
            height=35,
            command=self.destroy
        )
        back_btn.pack(side="left", padx=20, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"Student Details: {self.student.full_name}",
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=20, pady=30)
        
        # ===== CONTENT AREA (Scrollable) =====
        self.content_scroll = ctk.CTkScrollableFrame(main_frame, fg_color="#f0f2f5", corner_radius=0)
        self.content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ===== STUDENT INFORMATION CARD =====
        self.create_info_card("Student Information", self.get_student_info())
        
        # ===== GUARDIAN INFORMATION CARD =====
        self.create_info_card("Guardian Information", self.get_guardian_info())
        
        # ===== ACADEMIC INFORMATION CARD =====
        self.create_info_card("Academic Information", self.get_academic_info())
        
        # ===== FEE INFORMATION CARD =====
        self.create_info_card("Fee Information", self.get_fee_info())
        
        # ===== FEE RECORDS TABLE =====
        self.create_fee_records_table()
        
        # ===== CHALLANS TABLE =====
        self.create_challans_table()
    
    def create_info_card(self, title, data_dict):
        """Create an information card"""
        
        card = ctk.CTkFrame(self.content_scroll, fg_color="white", corner_radius=10)
        card.pack(fill="x", padx=10, pady=10)
        
        # Card title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        title_label.pack(pady=(15, 10), padx=20)
        
        # Info grid
        for key, value in data_dict.items():
            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill="x", padx=20, pady=5)
            
            key_label = ctk.CTkLabel(
                row_frame,
                text=f"{key}:",
                font=("Arial", 13, "bold"),
                text_color="#2c3e50",
                anchor="w",
                width=200
            )
            key_label.pack(side="left")
            
            value_label = ctk.CTkLabel(
                row_frame,
                text=value,
                font=("Arial", 13),
                text_color="#333333",
                anchor="w"
            )
            value_label.pack(side="left", padx=10)
    
    def create_fee_records_table(self):
        """Create fee records table"""
        
        table_card = ctk.CTkFrame(self.content_scroll, fg_color="white", corner_radius=10)
        table_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            table_card,
            text=f"Fee Records ({len(self.fee_records)})",
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        title_label.pack(pady=(15, 10))
        
        if not self.fee_records:
            empty_label = ctk.CTkLabel(
                table_card,
                text="No fee records found.",
                font=("Arial", 14),
                text_color="gray"
            )
            empty_label.pack(pady=20)
            return
        
        # Create table header
        headers = ["Date", "Type", "Amount", "Paid", "Remaining", "Status", "Receipt #"]
        widths = [100, 100, 100, 100, 100, 100, 120]
        
        header_frame = ctk.CTkFrame(table_card, fg_color="#1e3a5f")
        header_frame.pack(fill="x", padx=10)
        
        for header, width in zip(headers, widths):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 12, "bold"),
                text_color="white",
                width=width
            )
            label.pack(side="left", padx=2, pady=5)
        
        # Create rows
        for record in self.fee_records:
            row = ctk.CTkFrame(table_card, fg_color="#f8f9fa")
            row.pack(fill="x", padx=10, pady=2)
            
            values = [
                record.due_date.strftime("%Y-%m-%d") if record.due_date else "N/A",
                record.fee_type,
                f"Rs. {record.amount:.0f}",
                f"Rs. {record.paid_amount:.0f}",
                f"Rs. {record.remaining_amount:.0f}",
                record.status.value if record.status else "N/A",
                record.receipt_number or "N/A"
            ]
            
            for value, width in zip(values, widths):
                label = ctk.CTkLabel(
                    row,
                    text=value,
                    font=("Arial", 12),
                    text_color="#333333",
                    width=width,
                    anchor="center"
                )
                label.pack(side="left", padx=2, pady=5)
    
    def create_challans_table(self):
        """Create challans table"""
        
        table_card = ctk.CTkFrame(self.content_scroll, fg_color="white", corner_radius=10)
        table_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            table_card,
            text=f"Challans ({len(self.challans)})",
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        title_label.pack(pady=(15, 10))
        
        if not self.challans:
            empty_label = ctk.CTkLabel(
                table_card,
                text="No challans found.",
                font=("Arial", 14),
                text_color="gray"
            )
            empty_label.pack(pady=20)
            return
        
        # Create table header
        headers = ["Bill ID", "Month", "Total", "Paid", "Remaining", "Status", "Due Date"]
        widths = [120, 100, 100, 100, 100, 100, 100]
        
        header_frame = ctk.CTkFrame(table_card, fg_color="#1e3a5f")
        header_frame.pack(fill="x", padx=10)
        
        for header, width in zip(headers, widths):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 12, "bold"),
                text_color="white",
                width=width
            )
            label.pack(side="left", padx=2, pady=5)
        
        # Create rows
        for challan in self.challans:
            row = ctk.CTkFrame(table_card, fg_color="#f8f9fa")
            row.pack(fill="x", padx=10, pady=2)
            
            values = [
                challan.bill_id,
                f"{challan.challan_month} {challan.challan_year}",
                f"Rs. {challan.amount_due:.0f}",
                f"Rs. {challan.paid_amount:.0f}",
                f"Rs. {challan.remaining_amount:.0f}",
                challan.status,
                challan.due_date.strftime("%Y-%m-%d") if challan.due_date else "N/A"
            ]
            
            for value, width in zip(values, widths):
                label = ctk.CTkLabel(
                    row,
                    text=value,
                    font=("Arial", 12),
                    text_color="#333333",
                    width=width,
                    anchor="center"
                )
                label.pack(side="left", padx=2, pady=5)
    
    def get_student_info(self):
        """Get student personal information"""
        return {
            "Full Name": self.student.full_name,
            "Student ID": self.student.student_id,
            "Date of Birth": self.student.date_of_birth.strftime("%Y-%m-%d"),
            "Gender": self.student.gender.value,
            "CNIC/B-Form": self.student.cnic_bform or "N/A"
        }
    
    def get_guardian_info(self):
        """Get guardian information"""
        if not self.guardian:
            return {"Guardian": "N/A"}
        
        return {
            "Guardian Name": self.guardian.guardian_name,
            "Family ID": self.guardian.family_id,
            "CNIC": self.guardian.cnic or "N/A",
            "Mobile": self.guardian.mobile_number,
            "Email": self.guardian.email or "N/A",
            "Occupation": self.guardian.occupation or "N/A",
            "Monthly Income": f"Rs. {self.guardian.monthly_income:,.0f}" if self.guardian.monthly_income else "N/A",
            "Address": self.guardian.address or "N/A"
        }
    
    def get_academic_info(self):
        """Get academic information"""
        return {
            "Admission Date": self.student.admission_date.strftime("%Y-%m-%d"),
            "Class/Grade": self.student.class_grade,
            "Section": self.student.section or "N/A",
            "Status": self.student.academic_status.value if self.student.academic_status else "N/A"
        }
    
    def get_fee_info(self):
        """Get fee information"""
        return {
            "Monthly Fee": f"Rs. {self.student.monthly_tuition_fee:,.0f}",
            "Fee Concession": f"Rs. {self.student.fee_concession:,.0f}",
            "Total Outstanding": f"Rs. {self.student.total_outstanding_amount:,.0f}",
            "Last Payment Date": self.student.last_payment_date.strftime("%Y-%m-%d") if self.student.last_payment_date else "N/A",
            "Last Payment Amount": f"Rs. {self.student.last_payment_amount:,.0f}" if self.student.last_payment_amount else "N/A"
        }