"""
Principal Reports View - View Only
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from sqlalchemy import func
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.database.models import SessionLocal, Student, Guardian, FeeChallan

class PrincipalReportsView(ctk.CTkFrame):
    """Principal Reports View - Read Only"""
    
    def __init__(self, parent, db=None):
        super().__init__(parent)
        
        self.db = db if db else SessionLocal()
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create main UI widgets"""
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=100)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Reports & Analytics",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        # Reports Content Frame
        reports_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        reports_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Report Cards
        self.create_report_card(reports_frame, "Fee Collection Summary", 
            "View total billed, collected, and outstanding fees", 0, 0,
            self.view_fee_collection_report)
        
        self.create_report_card(reports_frame, "Outstanding Fees Report", 
            "View all families with unpaid challans", 0, 1,
            self.view_outstanding_report)
        
        self.create_report_card(reports_frame, "All Challans Report", 
            "View all generated fee challans", 1, 0,
            self.view_all_challans)
        
        self.create_report_card(reports_frame, "Student Enrollment Report", 
            "View all students with their class and fee info", 1, 1,
            self.view_student_enrollment_report)
        
        # Note
        note_label = ctk.CTkLabel(
            reports_frame,
            text="🔒 View Only Reports - Export functionality available to Admin only",
            font=("Arial", 14),
            text_color="gray"
        )
        note_label.grid(row=2, column=0, columnspan=2, pady=20)
    
    def create_report_card(self, parent, title, description, row, col, command=None):
        """Create a report card"""
        
        card = ctk.CTkFrame(
            parent,
            fg_color="#f8f9fa",
            corner_radius=10,
            border_width=1,
            border_color="#e0e0e0"
        )
        card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        title_label.pack(pady=(20, 10))
        
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=("Arial", 14),
            text_color="gray",
            wraplength=300
        )
        desc_label.pack(pady=10)
        
        if command:
            view_btn = ctk.CTkButton(
                card,
                text="View Report",
                font=("Arial", 13, "bold"),
                fg_color="#3498db",
                hover_color="#2980b9",
                width=150,
                height=40,
                command=command
            )
        else:
            view_btn = ctk.CTkButton(
                card,
                text="View Report",
                font=("Arial", 13, "bold"),
                fg_color="#3498db",
                hover_color="#2980b9",
                width=150,
                height=40,
                state="disabled"
            )
        view_btn.pack(pady=20)
    
    def view_fee_collection_report(self):
        """View Fee Collection Summary"""
        total_billed = self.db.query(FeeChallan).with_entities(
            func.sum(FeeChallan.total_amount)
        ).scalar() or 0
        
        total_collected = self.db.query(FeeChallan).with_entities(
            func.sum(FeeChallan.paid_amount)
        ).scalar() or 0
        
        total_outstanding = self.db.query(FeeChallan).with_entities(
            func.sum(FeeChallan.remaining_amount)
        ).scalar() or 0
        
        report_window = ctk.CTkToplevel(self)
        report_window.title("Fee Collection Report")
        report_window.geometry("600x400")
        
        report_frame = ctk.CTkFrame(report_window, fg_color="white", corner_radius=10)
        report_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        report_text = f"""
        FEE COLLECTION REPORT
        =====================
        
        Total Billed:        Rs. {total_billed:,.0f}
        Total Collected:     Rs. {total_collected:,.0f}
        Total Outstanding:   Rs. {total_outstanding:,.0f}
        
        =====================
        Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        report_label = ctk.CTkLabel(
            report_frame,
            text=report_text,
            font=("Arial", 16),
            text_color="#1e3a5f",
            justify="left"
        )
        report_label.pack(pady=50)
    
    def view_outstanding_report(self):
        """View Outstanding Fees"""
        challans = self.db.query(FeeChallan).filter(FeeChallan.remaining_amount > 0).all()
        
        if not challans:
            messagebox.showinfo("No Outstanding Fees", "No outstanding fees found!")
            return
        
        report_window = ctk.CTkToplevel(self)
        report_window.title("Outstanding Fees Report")
        report_window.geometry("900x600")
        
        scroll_frame = ctk.CTkScrollableFrame(report_window, fg_color="white")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            scroll_frame,
            text=f"Outstanding Fees ({len(challans)} challans)",
            font=("Arial", 20, "bold"),
            text_color="#1e3a5f"
        )
        title_label.pack(pady=10)
        
        for challan in challans:
            guardian = self.db.query(Guardian).filter(Guardian.family_id == challan.family_id).first()
            guardian_name = guardian.guardian_name if guardian else "N/A"
            
            challan_card = ctk.CTkFrame(scroll_frame, fg_color="#fdecea", corner_radius=8)
            challan_card.pack(fill="x", padx=10, pady=5)
            
            info_text = (
                f"Bill ID: {challan.bill_id} | Family: {challan.family_id} | "
                f"Guardian: {guardian_name} | Month: {challan.challan_month} {challan.challan_year} | "
                f"Outstanding: Rs. {challan.remaining_amount:,.0f}"
            )
            
            challan_label = ctk.CTkLabel(
                challan_card,
                text=info_text,
                font=("Arial", 13),
                text_color="#e74c3c",
                anchor="w"
            )
            challan_label.pack(side="left", padx=15, pady=10)
    
    def view_all_challans(self):
        """View All Challans"""
        challans = self.db.query(FeeChallan).order_by(FeeChallan.created_at.desc()).all()
        
        if not challans:
            messagebox.showinfo("No Challans", "No challans found!")
            return
        
        challan_window = ctk.CTkToplevel(self)
        challan_window.title("All Fee Challans")
        challan_window.geometry("1000x600")
        
        scroll_frame = ctk.CTkScrollableFrame(challan_window, fg_color="white")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            scroll_frame,
            text=f"All Fee Challans ({len(challans)})",
            font=("Arial", 20, "bold"),
            text_color="#1e3a5f"
        )
        title_label.pack(pady=10)
        
        for challan in challans:
            guardian = self.db.query(Guardian).filter(Guardian.family_id == challan.family_id).first()
            guardian_name = guardian.guardian_name if guardian else "N/A"
            
            if challan.is_paid:
                status = "PAID"
                status_color = "#2ecc71"
            elif challan.paid_amount > 0:
                status = "PARTIAL"
                status_color = "#f39c12"
            else:
                status = "UNPAID"
                status_color = "#e74c3c"
            
            challan_card = ctk.CTkFrame(scroll_frame, fg_color="#f8f9fa", corner_radius=8)
            challan_card.pack(fill="x", padx=10, pady=5)
            
            info_text = (
                f"Bill ID: {challan.bill_id} | Family: {challan.family_id} | "
                f"Guardian: {guardian_name} | Month: {challan.challan_month} {challan.challan_year} | "
                f"Amount: Rs. {challan.amount_due:,.0f} | "
                f"Paid: Rs. {challan.paid_amount:,.0f} | "
                f"Remaining: Rs. {challan.remaining_amount:,.0f}"
            )
            
            challan_label = ctk.CTkLabel(
                challan_card,
                text=info_text,
                font=("Arial", 12),
                text_color="#2c3e50",
                anchor="w"
            )
            challan_label.pack(side="left", padx=15, pady=10)
            
            status_label = ctk.CTkLabel(
                challan_card,
                text=status,
                font=("Arial", 12, "bold"),
                text_color=status_color
            )
            status_label.pack(side="right", padx=15, pady=10)
    
    def view_student_enrollment_report(self):
        """View Student Enrollment"""
        students = self.db.query(Student).all()
        
        if not students:
            messagebox.showinfo("No Students", "No students found!")
            return
        
        report_window = ctk.CTkToplevel(self)
        report_window.title("Student Enrollment Report")
        report_window.geometry("900x600")
        
        scroll_frame = ctk.CTkScrollableFrame(report_window, fg_color="white")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            scroll_frame,
            text=f"Student Enrollment ({len(students)} students)",
            font=("Arial", 20, "bold"),
            text_color="#1e3a5f"
        )
        title_label.pack(pady=10)
        
        for student in students:
            guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
            family_id = guardian.family_id if guardian else "N/A"
            
            student_card = ctk.CTkFrame(scroll_frame, fg_color="#f8f9fa", corner_radius=8)
            student_card.pack(fill="x", padx=10, pady=5)
            
            info_text = (
                f"{student.full_name} | ID: {student.student_id} | "
                f"Family: {family_id} | Class: {student.class_grade} | "
                f"Fee: Rs. {student.monthly_tuition_fee:,.0f} | "
                f"Concession: Rs. {student.fee_concession:,.0f}"
            )
            
            student_label = ctk.CTkLabel(
                student_card,
                text=info_text,
                font=("Arial", 13),
                text_color="#2c3e50",
                anchor="w"
            )
            student_label.pack(side="left", padx=15, pady=10)
