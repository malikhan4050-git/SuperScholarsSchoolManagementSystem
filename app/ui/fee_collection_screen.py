"""
Fee Collection Screen - Record Payment
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import date, datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal, FeeChallan, Student, Guardian, FeeStatus, PaymentMethod, FeeRecord
from app.services.fee_service import FeeService
from app.utils.id_generator import IDGenerator


class FeeCollectionScreen(ctk.CTkToplevel):
    """Fee Collection Screen - Professional & Clean"""
    
    def __init__(self, parent, db=None):
        super().__init__(parent)
        
        self.title("Fee Collection Screen")
        self.geometry("1000x750")
        self.minsize(900, 650)
        
        self.db = db if db else SessionLocal()
        self.fee_service = FeeService(self.db)
        self.id_generator = IDGenerator()
        
        self.current_challan = None
        
        # Create UI
        self.create_widgets()
        
        # Make modal
        self.transient(parent)
    
    def create_widgets(self):
        """Create main UI widgets - Professional Layout"""
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        main_frame.pack(fill="both", expand=True)
        
        # ===== HEADER (Orange Background) =====
        header_frame = ctk.CTkFrame(main_frame, fg_color="#e67e22", corner_radius=0, height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_title = ctk.CTkLabel(
            header_frame,
            text="Fee Collection Screen",
            font=("Arial", 22, "bold"),
            text_color="white"
        )
        header_title.pack(side="left", padx=20, pady=15)
        
        # ===== FILTER SECTION =====
        filter_frame = ctk.CTkFrame(main_frame, fg_color="#f8f9fa", corner_radius=0)
        filter_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        filter_label = ctk.CTkLabel(
            filter_frame,
            text="Search by Bill ID:",
            font=("Arial", 16, "bold"),
            text_color="#2c3e50"
        )
        filter_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Search row
        search_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_row.pack(fill="x", padx=20, pady=(0, 15))
        
        self.filter_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Enter Bill ID (e.g., FM2600001-JAN)",
            font=("Arial", 14),
            height=45,
            width=500,
            border_color="#bdc3c7",
            fg_color="white"
        )
        self.filter_entry.pack(side="left", padx=(0, 10))
        self.filter_entry.bind("<Return>", lambda e: self.search_challan())
        
        search_btn = ctk.CTkButton(
            search_row,
            text="Search",
            font=("Arial", 14, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            width=120,
            height=45,
            command=self.search_challan
        )
        search_btn.pack(side="left")
        
        # ===== STUDENT INFO SECTION =====
        info_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10, border_width=1, border_color="#e0e0e0")
        info_frame.pack(fill="x", padx=30, pady=10)
        
        self.student_label = ctk.CTkLabel(
            info_frame,
            text="No challan selected",
            font=("Arial", 18, "bold"),
            text_color="#2c3e50"
        )
        self.student_label.pack(pady=15)
        
        # ===== DETAILS GRID =====
        details_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10, border_width=1, border_color="#e0e0e0")
        details_frame.pack(fill="both", expand=True, padx=30, pady=10)
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)
        details_frame.grid_rowconfigure(0, weight=1)
        details_frame.grid_rowconfigure(1, weight=1)
        
        # LEFT SIDE - Labels
        left_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Select Date
        date_label = ctk.CTkLabel(
            left_frame,
            text="Select Date:",
            font=("Arial", 14, "bold"),
            text_color="#2c3e50"
        )
        date_label.pack(anchor="w", pady=(0, 5))
        
        self.date_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="YYYY-MM-DD",
            font=("Arial", 14),
            height=40,
            width=200,
            justify="center",
            border_color="#bdc3c7",
            fg_color="white"
        )
        self.date_entry.pack(anchor="w", pady=(0, 15))
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # Total Fees
        total_label = ctk.CTkLabel(
            left_frame,
            text="Total Fees:",
            font=("Arial", 14, "bold"),
            text_color="#2c3e50"
        )
        total_label.pack(anchor="w", pady=(0, 5))
        
        self.total_value = ctk.CTkLabel(
            left_frame,
            text="Rs. 0",
            font=("Arial", 24, "bold"),
            text_color="#2ecc71"
        )
        self.total_value.pack(anchor="w", pady=(0, 15))
        
        # RIGHT SIDE - Editable fields
        right_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Paid Amount
        paid_label = ctk.CTkLabel(
            right_frame,
            text="Paid Amount:",
            font=("Arial", 14, "bold"),
            text_color="#2c3e50"
        )
        paid_label.pack(anchor="w", pady=(0, 5))
        
        self.paid_entry = ctk.CTkEntry(
            right_frame,
            placeholder_text="Enter amount paid",
            font=("Arial", 14),
            height=40,
            width=200,
            justify="right",
            border_color="#bdc3c7",
            fg_color="white"
        )
        self.paid_entry.pack(anchor="w", pady=(0, 15))
        
        # Remaining
        remaining_label = ctk.CTkLabel(
            right_frame,
            text="Remaining:",
            font=("Arial", 14, "bold"),
            text_color="#2c3e50"
        )
        remaining_label.pack(anchor="w", pady=(0, 5))
        
        self.remaining_value = ctk.CTkLabel(
            right_frame,
            text="Rs. 0",
            font=("Arial", 24, "bold"),
            text_color="#e74c3c"
        )
        self.remaining_value.pack(anchor="w", pady=(0, 15))
        
        # Bind paid entry to update remaining
        self.paid_entry.bind("<KeyRelease>", self.update_remaining)
        
        # ===== BUTTONS =====
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Payment",
            font=("Arial", 16, "bold"),
            fg_color="#27ae60",
            hover_color="#229954",
            width=250,
            height=50,
            command=self.save_payment
        )
        save_btn.pack(side="left", padx=10)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            font=("Arial", 14, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=120,
            height=50,
            command=self.destroy
        )
        close_btn.pack(side="left", padx=10)
    
    def search_challan(self):
        """Search for a challan by Bill ID only"""
        
        search_term = self.filter_entry.get().strip()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter Bill ID!")
            return
        
        # Search by Bill ID only
        challan = self.db.query(FeeChallan).filter(FeeChallan.bill_id == search_term).first()
        
        if not challan:
            messagebox.showerror("Error", "No challan found with this Bill ID!")
            return
        
        # Check if already paid
        if challan.status == "PAID":
            messagebox.showinfo("Already Paid", 
                f"This challan has already been paid!\n\n"
                f"Bill ID: {challan.bill_id}\n"
                f"Paid Amount: Rs. {challan.paid_amount:.0f}\n"
                f"Payment Date: {challan.payment_date}"
            )
            return
        
        # Store current challan
        self.current_challan = challan
        
        # Get student and guardian
        student = self.db.query(Student).filter(Student.id == challan.student_id).first()
        guardian = self.db.query(Guardian).filter(Guardian.family_id == challan.family_id).first()
        
        # Update UI - Show Student ID as well
        if student and guardian:
            self.student_label.configure(
                text=f"Student: {student.first_name} {student.last_name} (ID: {student.student_id}) | Father: {guardian.guardian_name}"
            )
        
        # Update total fees (amount_due)
        total = challan.amount_due
        self.total_value.configure(text=f"Rs. {total:.0f}")
        
        # Update remaining (amount_due - paid_amount)
        remaining = challan.amount_due - challan.paid_amount
        self.remaining_value.configure(text=f"Rs. {remaining:.0f}")
    
    def update_remaining(self, event=None):
        """Update remaining amount based on paid amount"""
        
        if not self.current_challan:
            return
        
        try:
            paid_amount = float(self.paid_entry.get()) if self.paid_entry.get() else 0
            total = self.current_challan.amount_due
            remaining = total - paid_amount
            
            if remaining < 0:
                remaining = 0
            
            self.remaining_value.configure(text=f"Rs. {remaining:.0f}")
        except ValueError:
            pass
    
    def save_payment(self):
        """Save the payment"""
        
        if not self.current_challan:
            messagebox.showwarning("Warning", "Please search for a challan first!")
            return
        
        try:
            # Get paid amount
            paid_amount = float(self.paid_entry.get())
            
            if not paid_amount or paid_amount <= 0:
                messagebox.showwarning("Warning", "Please enter a valid paid amount!")
                return
            
            # Get date
            try:
                payment_date = datetime.strptime(self.date_entry.get(), "%Y-%m-%d").date()
            except ValueError:
                payment_date = date.today()
            
            # Update challan
            challan = self.current_challan
            challan.paid_amount += paid_amount
            challan.remaining_amount = challan.amount_due - challan.paid_amount
            challan.payment_date = payment_date
            challan.payment_method = PaymentMethod.CASH.value
            challan.receipt_number = self.id_generator.generate_receipt_number()
            
            # Update status based on payment
            if challan.paid_amount >= challan.amount_due:
                challan.status = "PAID"
            elif challan.paid_amount > 0:
                challan.status = "PARTIAL"
            else:
                challan.status = "PENDING"
            
            # Create a FeeRecord entry
            fee_record = FeeRecord(
                student_id=challan.student_id,
                fee_type="Monthly",
                amount=challan.amount_due,
                paid_amount=paid_amount,
                remaining_amount=challan.remaining_amount,
                due_date=payment_date,
                paid_date=payment_date,
                status=FeeStatus.PAID if challan.paid_amount >= challan.amount_due else FeeStatus.PARTIAL,
                payment_method=PaymentMethod.CASH,
                receipt_number=challan.receipt_number,
                description=f"Payment for {challan.challan_month}"
            )
            self.db.add(fee_record)
            
            # Update student's total outstanding
            student = self.db.query(Student).filter(Student.id == challan.student_id).first()
            if student:
                student.total_outstanding_amount = challan.remaining_amount
                student.last_payment_date = payment_date
                student.last_payment_amount = paid_amount
            
            # Commit
            self.db.commit()
            
            # Notify parent to refresh summary
            if hasattr(self.master, 'refresh_summary'):
                self.master.refresh_summary()
            
            messagebox.showinfo(
                "Success",
                f"Payment recorded successfully!\n\n"
                f"Receipt Number: {challan.receipt_number}\n"
                f"Paid Amount: Rs. {paid_amount:.0f}\n"
                f"Remaining: Rs. {challan.remaining_amount:.0f}"
            )
            
            # Reset form
            self.filter_entry.delete(0, "end")
            self.paid_entry.delete(0, "end")
            self.student_label.configure(text="No challan selected")
            self.total_value.configure(text="Rs. 0")
            self.remaining_value.configure(text="Rs. 0")
            self.current_challan = None
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Failed to save payment: {str(e)}")