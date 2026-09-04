"""
Fee Challan Generation Screen for Super Scholars School Management System
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.database.models import SessionLocal, Student, Guardian, FeeChallan
from app.services.fee_service import FeeService
from app.ui.challan_preview_window import ChallanPreviewWindow

class FeeChallanlScreen(ctk.CTkFrame):
    """Fee Challan Generation Screen with Month Dropdown in Header"""
    
    def __init__(self, parent, db: Session = None):
        super().__init__(parent)
        
        # Database
        self.db = db if db else SessionLocal()
        self.fee_service = FeeService(self.db)
        
        # Store data
        self.families_data = []
        self.selected_families = []
        self.table_rows = []
        self.current_month = "January"
        
        # Cache for arrears (family_id -> total_arrears)
        self.arrears_cache = {}
        
        # Create UI
        self.create_widgets()
        self.load_families_data()
    
    def create_widgets(self):
        """Create main UI widgets"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        self.create_header()
        
        # Search and Controls Frame
        self.create_search_controls()
        
        # Table Frame
        self.create_table()
        
        # Buttons Frame
        self.create_buttons()
    
    def create_header(self):
        """Create header section"""
        
        header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Generate Fee Challan",
            font=("Arial", 28, "bold"),
            text_color="#1e3a5f"
        )
        title.pack(side="left", padx=10, pady=20)
    
    def create_search_controls(self):
        """Create search and control widgets"""
        
        control_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # ===== SEARCH SECTION =====
        search_label = ctk.CTkLabel(
            control_frame,
            text="Search:",
            font=("Arial", 14, "bold"),
            text_color="#1e3a5f"
        )
        search_label.pack(side="left", padx=(20, 10), pady=15)
        
        self.search_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="Search by Student/Family ID or Name...",
            font=("Arial", 13),
            height=40,
            width=400,
            border_color="#bdc3c7",
            fg_color="#f8f9fa"
        )
        self.search_entry.pack(side="left", padx=10, pady=15)
        self.search_entry.bind("<Return>", lambda e: self.search_families())
        
        self.search_btn = ctk.CTkButton(
            control_frame,
            text="Search",
            font=("Arial", 12, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            width=100,
            height=40,
            command=self.search_families
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
    
    def create_table(self):
        """Create a fixed-width table using Frames (No Horizontal Scroll)"""
        
        # Main table container
        table_container = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Define column widths (FIXED - no overlap possible)
        # New order: Checkbox, Family ID, Students, Student IDs, Month, Monthly Fee, Concession, Arrears, Admission, Registration, Exam, Transport, Other, Total
        self.col_widths = [60, 140, 220, 200, 120, 130, 110, 120, 100, 110, 100, 110, 100, 120]
        self.headers = ["✓", "Family ID", "Student(s)", "Student ID(s)", "Month", 
                       "Monthly Fee", "Concession", "Arrears", "Admission", 
                       "Registration", "Exam", "Transport", "Other", "Total for Month"]
        
        # Create header row
        header_row = ctk.CTkFrame(table_container, fg_color="#1e3a5f", height=70)
        header_row.pack(fill="x", pady=(0, 4))
        header_row.pack_propagate(False)
        
        for i, (header_text, width) in enumerate(zip(self.headers, self.col_widths)):
            # Create a fixed-width frame for each header cell with padding
            cell_frame = ctk.CTkFrame(header_row, fg_color="#1e3a5f", width=width + 10, height=70)
            cell_frame.pack(side="left", padx=2, pady=0)
            cell_frame.pack_propagate(False)
            
            # SPECIAL: For Month column (index 4), add heading + dropdown
            if i == 4:
                month_heading = ctk.CTkLabel(
                    cell_frame,
                    text="Month",
                    font=("Arial", 11, "bold"),
                    text_color="white",
                    anchor="center"
                )
                month_heading.pack(pady=(5, 2))
                
                self.header_month_var = ctk.StringVar(value=self.current_month)
                month_dropdown = ctk.CTkOptionMenu(
                    cell_frame,
                    values=["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"],
                    variable=self.header_month_var,
                    width=width - 10,
                    height=28,
                    font=("Arial", 11, "bold"),
                    fg_color="#2980b9",
                    button_color="#1e6fa8",
                    text_color="white",
                    command=self.on_month_change
                )
                month_dropdown.pack(pady=(0, 5))
            else:
                header_label = ctk.CTkLabel(
                    cell_frame,
                    text=header_text,
                    font=("Arial", 12, "bold"),
                    text_color="white",
                    anchor="center",
                    justify="center",
                    wraplength=width - 10
                )
                header_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollable area for rows (Vertical only)
        self.scroll_frame = ctk.CTkScrollableFrame(
            table_container,
            fg_color="white",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, pady=(2, 0))
        
        # Store row references
        self.row_frames = []
    
    def on_month_change(self, month):
        """Handle month change from header dropdown"""
        self.current_month = month
        
        # Recalculate arrears for ALL families (efficiently)
        self.load_arrears_for_month(month)
        
        # Update ALL row data and displays
        for row_data in self.table_rows:
            row_data['month'] = month
            
            # Get cached arrears for this family
            family_id = row_data['family_id']
            total_family_arrears = self.arrears_cache.get(family_id, 0)
            row_data['arrears'] = total_family_arrears
            
            # Update the arrears display label
            if 'arrears_label' in row_data and row_data['arrears_label'] is not None:
                row_data['arrears_label'].configure(text=f"Rs. {total_family_arrears:,.0f}")
                row_data['arrears_label'].update_idletasks()
            
            # Update the month display label
            if 'month_display' in row_data and row_data['month_display'] is not None:
                row_data['month_display'].configure(text=month)
                row_data['month_display'].update_idletasks()
            
            # Recalculate total for this month
            self.update_row_total(row_data)
        
        print(f"Month '{month}' applied to all {len(self.table_rows)} rows")
        print(f"   Updated: {[r['month'] for r in self.table_rows]}")
    
    def load_arrears_for_month(self, month):
        """Efficiently load all arrears for a given month in ONE query"""
        self.arrears_cache = {}
        
        # Define month order
        month_order = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        
        current_month_num = month_order.get(month, 1)
        
        # Get ALL challans from PREVIOUS months for ALL families
        all_challans = self.db.query(FeeChallan).all()
        
        # Group by family_id and sum exact_payable for previous months
        for challan in all_challans:
            challan_month = challan.challan_month
            challan_month_num = month_order.get(challan_month, 1)
            
            # Only count challans from months BEFORE the current month
            if challan_month_num < current_month_num:
                family_id = challan.family_id
                if family_id not in self.arrears_cache:
                    self.arrears_cache[family_id] = 0
                # Use exact_payable if not paid
                if not challan.is_paid:
                    self.arrears_cache[family_id] += challan.exact_payable
    
    def load_families_data(self):
        """Load all families with students from database"""
        
        try:
            self.families_data = self.fee_service.get_all_families_with_students()
            
            # Pre-load arrears for current month
            self.load_arrears_for_month(self.current_month)
            
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load families: {str(e)}")
    
    def refresh_table(self, families_data=None):
        """Refresh table with current families data"""
        
        # Clear existing data rows
        for row_frame in self.row_frames:
            row_frame.destroy()
        self.row_frames = []
        
        self.table_rows = []
        self.selected_families = []
        
        # Use provided data or all data
        data_to_display = families_data if families_data is not None else self.families_data
        
        if not data_to_display:
            empty_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No students found. Please add students first.",
                font=("Arial", 16),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        
        # Create rows for each family
        for idx, family_data in enumerate(data_to_display):
            self.create_family_row(family_data, idx)
        
        # Reset Select All checkbox
        self.check_all_var.set(False)
    
    def create_family_row(self, family_data, row_idx):
        """Create a row with fixed-width cells"""
        
        students = family_data['students']
        student_names = ", ".join([f"{s.first_name} {s.last_name}" for s in students])
        student_ids = ", ".join([s.student_id for s in students])
        
        # Get cached arrears for this family
        family_id = family_data['family_id']
        total_family_arrears = self.arrears_cache.get(family_id, 0)
        total_family_concession = sum(s.fee_concession for s in students)
        
        # Create row data
        row_data = {
            'family_id': family_id,
            'guardian_name': family_data.get('guardian_name', ''),
            'guardian_cnic': family_data.get('guardian_cnic', ''),
            'students': students,
            'monthly_fee': family_data['total_monthly_fee'],
            'month': self.current_month,
            'admission_fee': 0,
            'registration_fee': 0,
            'exam_fee': 0,
            'transport_fee': 0,
            'arrears': total_family_arrears,
            'fee_concession': total_family_concession,
            'other_fee': 0,
            'total_for_month': 0,  # New field for total
            'checked': False,
            'month_display': None,
            'arrears_label': None,
            'total_label': None,  # New field for total label
            'editable_entries': []  # Store editable entries for recalculation
        }
        
        # Create row frame with fixed height
        row_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#f8f9fa" if row_idx % 2 == 0 else "white",
            height=60
        )
        row_frame.pack(fill="x", pady=2)
        row_frame.pack_propagate(False)
        
        # Column 0: Checkbox
        cell_0 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[0] + 10)
        cell_0.pack(side="left", padx=2)
        cell_0.pack_propagate(False)
        
        check_var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(
            cell_0,
            text="",
            variable=check_var,
            width=30,
            command=lambda r=row_data, c=check_var: self.toggle_row_check(r, c)
        )
        checkbox.pack(pady=15)
        
        # Column 1: Family ID
        cell_1 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[1] + 10)
        cell_1.pack(side="left", padx=2)
        cell_1.pack_propagate(False)
        
        family_label = ctk.CTkLabel(
            cell_1,
            text=family_id,
            font=("Arial", 12, "bold"),
            text_color="#1e3a5f",
            anchor="w",
            wraplength=self.col_widths[1]
        )
        family_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Column 2: Students
        cell_2 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[2] + 10)
        cell_2.pack(side="left", padx=2)
        cell_2.pack_propagate(False)
        
        student_label = ctk.CTkLabel(
            cell_2,
            text=student_names,
            font=("Arial", 11),
            text_color="#2c3e50",
            anchor="w",
            wraplength=self.col_widths[2]
        )
        student_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Column 3: Student IDs
        cell_3 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[3] + 10)
        cell_3.pack(side="left", padx=2)
        cell_3.pack_propagate(False)
        
        student_ids_label = ctk.CTkLabel(
            cell_3,
            text=student_ids,
            font=("Arial", 11),
            text_color="#2c3e50",
            anchor="w",
            wraplength=self.col_widths[3]
        )
        student_ids_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Column 4: Month
        cell_4 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[4] + 10)
        cell_4.pack(side="left", padx=2)
        cell_4.pack_propagate(False)
        
        month_display = ctk.CTkLabel(
            cell_4,
            text=self.current_month,
            font=("Arial", 12, "bold"),
            text_color="#2c3e50",
            anchor="center"
        )
        month_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        row_data['month_display'] = month_display
        
        # Column 5: Monthly Fee (Green, Disabled)
        cell_5 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[5] + 10)
        cell_5.pack(side="left", padx=2)
        cell_5.pack_propagate(False)
        
        monthly_fee_label = ctk.CTkLabel(
            cell_5,
            text=f"Rs. {row_data['monthly_fee']:,.0f}",
            font=("Arial", 12, "bold"),
            text_color="#2ecc71",
            fg_color="#e8f8f5",
            corner_radius=3,
            anchor="center"
        )
        monthly_fee_label.pack(fill="both", expand=True, padx=5, pady=15)
        
        # Column 6: Concession (Purple, Disabled)
        cell_6 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[6] + 10)
        cell_6.pack(side="left", padx=2)
        cell_6.pack_propagate(False)
        
        concession_label = ctk.CTkLabel(
            cell_6,
            text=f"Rs. {row_data['fee_concession']:,.0f}",
            font=("Arial", 12, "bold"),
            text_color="#8e44ad",
            fg_color="#f5eef8",
            corner_radius=3,
            anchor="center"
        )
        concession_label.pack(fill="both", expand=True, padx=5, pady=15)
        
        # Column 7: Arrears (Red, Disabled)
        cell_7 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[7] + 10)
        cell_7.pack(side="left", padx=2)
        cell_7.pack_propagate(False)
        
        arrears_label = ctk.CTkLabel(
            cell_7,
            text=f"Rs. {row_data['arrears']:,.0f}",
            font=("Arial", 12, "bold"),
            text_color="#e74c3c",
            fg_color="#fdecea",
            corner_radius=3,
            anchor="center"
        )
        arrears_label.pack(fill="both", expand=True, padx=5, pady=15)
        row_data['arrears_label'] = arrears_label
        
        # Columns 8-11: Admission, Registration, Exam, Transport (Editable)
        editable_fields = ['admission_fee', 'registration_fee', 'exam_fee', 'transport_fee']
        for col_idx, field_name in enumerate(editable_fields, start=8):
            cell = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[col_idx] + 10)
            cell.pack(side="left", padx=2)
            cell.pack_propagate(False)
            
            entry = ctk.CTkEntry(
                cell,
                width=self.col_widths[col_idx],
                height=30,
                font=("Arial", 11),
                justify="center",
                placeholder_text="0",
                border_color="#bdc3c7",
                fg_color="white"
            )
            entry.insert(0, "0")
            entry.pack(pady=15)
            entry.bind("<KeyRelease>", lambda e, r=row_data, f=field_name, ent=entry: self.update_editable_fee(r, f, ent))
            row_data['editable_entries'].append(entry)
        
        # Column 12: Other (Editable)
        cell_12 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[12] + 10)
        cell_12.pack(side="left", padx=2)
        cell_12.pack_propagate(False)
        
        other_entry = ctk.CTkEntry(
            cell_12,
            width=self.col_widths[12],
            height=30,
            font=("Arial", 11),
            justify="center",
            placeholder_text="0",
            border_color="#bdc3c7",
            fg_color="white"
        )
        other_entry.insert(0, "0")
        other_entry.pack(pady=15)
        other_entry.bind("<KeyRelease>", lambda e, r=row_data, ent=other_entry: self.update_editable_fee(r, 'other_fee', ent))
        row_data['editable_entries'].append(other_entry)
        
        # Column 13: Total for Month (Auto-calculated)
        cell_13 = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.col_widths[13] + 10)
        cell_13.pack(side="left", padx=2)
        cell_13.pack_propagate(False)
        
        total_label = ctk.CTkLabel(
            cell_13,
            text="Rs. 0",
            font=("Arial", 12, "bold"),
            text_color="#1e3a5f",
            fg_color="#e3f2fd",
            corner_radius=3,
            anchor="center"
        )
        total_label.pack(fill="both", expand=True, padx=5, pady=15)
        row_data['total_label'] = total_label
        
        # Calculate initial total
        self.update_row_total(row_data)
        
        # Store reference
        row_data['checkbox'] = check_var
        row_data['row_frame'] = row_frame
        self.table_rows.append(row_data)
        self.row_frames.append(row_frame)
    
    def update_editable_fee(self, row_data, field_name, entry):
        """Update editable fee field and recalculate total"""
        try:
            value = float(entry.get()) if entry.get() else 0.0
            row_data[field_name] = value
            self.update_row_total(row_data)
        except ValueError:
            entry.delete(0, "end")
            entry.insert(0, "0")
            row_data[field_name] = 0.0
            self.update_row_total(row_data)
    
    def update_row_total(self, row_data):
        """Calculate and update the total for this month"""
        # Formula: Monthly Fee - Concession + Arrears + Editable Fees
        total = (row_data['monthly_fee'] 
                 - row_data['fee_concession'] 
                 + row_data['arrears'] 
                 + row_data['admission_fee'] 
                 + row_data['registration_fee'] 
                 + row_data['exam_fee'] 
                 + row_data['transport_fee'] 
                 + row_data['other_fee'])
        
        row_data['total_for_month'] = total
        
        if 'total_label' in row_data and row_data['total_label'] is not None:
            row_data['total_label'].configure(text=f"Rs. {total:,.0f}")
            row_data['total_label'].update_idletasks()
    
    def toggle_row_check(self, row_data, check_var):
        row_data['checked'] = check_var.get()
        
        if row_data['checked']:
            if row_data not in self.selected_families:
                self.selected_families.append(row_data)
        else:
            if row_data in self.selected_families:
                self.selected_families.remove(row_data)
        
        self.update_check_all_state()
    
    def toggle_check_all(self):
        checked = self.check_all_var.get()
        self.selected_families = []
        
        for row_data in self.table_rows:
            row_data['checked'] = checked
            row_data['checkbox'].set(checked)
            
            if checked:
                self.selected_families.append(row_data)
    
    def update_check_all_state(self):
        total_rows = len(self.table_rows)
        checked_rows = sum(1 for row in self.table_rows if row['checked'])
        
        if checked_rows == 0:
            self.check_all_var.set(False)
        elif checked_rows == total_rows:
            self.check_all_var.set(True)
    
    def search_families(self):
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.refresh_table()
            return
        
        filtered_families = []
        for family_data in self.families_data:
            if (search_term.lower() in family_data['family_id'].lower() or
                any(search_term.lower() in f"{s.first_name} {s.last_name}".lower() 
                    for s in family_data['students']) or
                any(search_term.lower() in s.student_id.lower() 
                    for s in family_data['students'])):
                filtered_families.append(family_data)
        
        self.refresh_table(filtered_families)
    
    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.refresh_table()
    
    def create_buttons(self):
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        generate_btn = ctk.CTkButton(
            button_frame,
            text="Generate Challan(s)",
            font=("Arial", 14, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=250,
            height=50,
            command=self.generate_challans
        )
        generate_btn.pack(side="left", padx=10)
    
    def generate_challans(self):
        if not self.selected_families:
            messagebox.showwarning("No Selection", "Please select at least one family!")
            return
        
        try:
            challans_data = []
            
            for row_data in self.selected_families:
                family_challan_data = {
                    'family_id': row_data['family_id'],
                    'guardian_name': row_data.get('guardian_name', ''),
                    'guardian_cnic': row_data.get('guardian_cnic', ''),
                    'challan_month': self.current_month,
                    'students': row_data['students'],
                    'total_monthly_tuition_fee': row_data['monthly_fee'],
                    'total_concession': row_data['fee_concession'],
                    'total_arrears': row_data['arrears'],
                    'admission_fee': row_data['admission_fee'],
                    'registration_fee': row_data['registration_fee'],
                    'exam_fee': row_data['exam_fee'],
                    'transport_fee': row_data['transport_fee'],
                    'other_fee': row_data['other_fee'],
                    'exact_payable': row_data['total_for_month']  # Use the calculated total
                }
                challans_data.append(family_challan_data)
            
            if not challans_data:
                messagebox.showwarning("No Data", "No families found for selected rows!")
                return
            
            preview_window = ChallanPreviewWindow(self, challans_data, self.db, self.fee_service)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate challans: {str(e)}")
    
    def print_challans(self, count: int):
        pass