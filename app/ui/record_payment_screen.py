"""
Record Payment Screen - Admin Dashboard
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import date, datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal, FeeChallan, Student, Guardian, FeeStatus, PaymentMethod
from app.services.fee_service import FeeService
from app.utils.id_generator import IDGenerator


class RecordPaymentScreen(ctk.CTkFrame):
    """Record Payment Screen with two main buttons"""
    
    def __init__(self, parent, db=None):
        super().__init__(parent)
        
        # Database
        self.db = db if db else SessionLocal()
        self.fee_service = FeeService(self.db)
        self.id_generator = IDGenerator()
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create main UI widgets"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=80)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Record Payment",
            font=("Arial", 24, "bold"),
            text_color="#1e3a5f"
        )
        title.pack(side="left", padx=30, pady=20)
        
        # Main Content Area
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=30)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # ===== Button 1: Record Payment =====
        record_card = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=15, border_width=1, border_color="#e0e0e0")
        record_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        record_title = ctk.CTkLabel(
            record_card,
            text="Record Payment",
            font=("Arial", 22, "bold"),
            text_color="#1e3a5f"
        )
        record_title.pack(pady=(40, 10))
        
        record_desc = ctk.CTkLabel(
            record_card,
            text="Record a new payment against\nan existing fee challan",
            font=("Arial", 13),
            text_color="gray",
            justify="center"
        )
        record_desc.pack(pady=10)
        
        record_btn = ctk.CTkButton(
            record_card,
            text="Open Fee Collection",
            font=("Arial", 14, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=250,
            height=50,
            command=self.open_fee_collection
        )
        record_btn.pack(pady=30)
        
        # ===== Button 2: View Payment Details =====
        view_card = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=15, border_width=1, border_color="#e0e0e0")
        view_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        view_title = ctk.CTkLabel(
            view_card,
            text="View Payment Details",
            font=("Arial", 22, "bold"),
            text_color="#1e3a5f"
        )
        view_title.pack(pady=(40, 10))
        
        view_desc = ctk.CTkLabel(
            view_card,
            text="View summary of paid and\nunpaid payments for any month",
            font=("Arial", 13),
            text_color="gray",
            justify="center"
        )
        view_desc.pack(pady=10)
        
        view_btn = ctk.CTkButton(
            view_card,
            text="Open Summary",
            font=("Arial", 14, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            width=250,
            height=50,
            command=self.open_summary
        )
        view_btn.pack(pady=30)
    
    def open_fee_collection(self):
        """Open the Fee Collection Screen"""
        from app.ui.fee_collection_screen import FeeCollectionScreen
        FeeCollectionScreen(self, self.db)
    
    def open_summary(self):
        """Open the Summary Screen"""
        from app.ui.payment_summary_screen import PaymentSummaryScreen
        PaymentSummaryScreen(self, self.db)