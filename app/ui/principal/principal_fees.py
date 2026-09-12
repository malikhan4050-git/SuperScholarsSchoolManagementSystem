"""
Principal Fees View - View Only
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from sqlalchemy import func

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.database.models import SessionLocal, Guardian, FeeChallan

class PrincipalFeesView(ctk.CTkFrame):
    """Principal Fees View - Read Only"""
    
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
            text="Fee Management (View Only)",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        self.header_title.pack(side="left", padx=30, pady=30)
        
        # Summary Frame
        summary_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        summary_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Calculate from FeeChallan
        total_billed = self.db.query(FeeChallan).with_entities(
            func.sum(FeeChallan.total_amount)
        ).scalar() or 0
        
        total_collected = self.db.query(FeeChallan).with_entities(
            func.sum(FeeChallan.paid_amount)
        ).scalar() or 0
        
        total_outstanding = self.db.query(FeeChallan).with_entities(
            func.sum(FeeChallan.remaining_amount)
        ).scalar() or 0
        
        # Display summary
        summary_text = f"""
        Fee Summary:
        ============
        Total Billed:        Rs. {total_billed:,.0f}
        Total Collected:     Rs. {total_collected:,.0f}
        Total Outstanding:   Rs. {total_outstanding:,.0f}
        """
        
        summary_label = ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=("Arial", 18),
            text_color="#1e3a5f",
            justify="left"
        )
        summary_label.pack(pady=50)
        
        # View Challans button
        view_challans_btn = ctk.CTkButton(
            summary_frame,
            text="View All Challans",
            font=("Arial", 14, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            width=200,
            height=45,
            command=self.view_all_challans
        )
        view_challans_btn.pack(pady=20)
        
        # Note
        note_label = ctk.CTkLabel(
            summary_frame,
            text="🔒 View Only - Contact Admin for fee management actions",
            font=("Arial", 14),
            text_color="gray"
        )
        note_label.pack(pady=10)
    
    def view_all_challans(self):
        """View all challans"""
        challans = self.db.query(FeeChallan).order_by(FeeChallan.created_at.desc()).all()
        
        if not challans:
            messagebox.showinfo("No Challans", "No challans found!")
            return
        
        # Create window
        challan_window = ctk.CTkToplevel(self)
        challan_window.title("All Fee Challans (View Only)")
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
        
        # Show each challan
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
