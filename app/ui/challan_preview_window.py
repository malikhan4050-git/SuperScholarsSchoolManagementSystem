"""
Challan Preview Window - FAST & LIGHTWEIGHT
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import date, datetime
import os
from pathlib import Path

# Import models
from app.database.models import SessionLocal, FeeChallan

class ChallanPreviewWindow(ctk.CTkToplevel):
    """Window for previewing challans - FAST version"""
    
    def __init__(self, parent, challans_data, db, fee_service):
        super().__init__(parent)
        
        self.title("Fee Challan Preview")
        self.geometry("1000x600")
        self.challans_data = challans_data
        self.db = db
        self.fee_service = fee_service
        
        # Create challans directory if it doesn't exist
        self.challans_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "challans"
        )
        Path(self.challans_dir).mkdir(exist_ok=True)
        
        # Calculate pages needed
        self.total_challans = len(challans_data)
        self.challans_per_page = 4
        self.total_pages = (self.total_challans + self.challans_per_page - 1) // self.challans_per_page
        
        # Store generated challan IDs
        self.generated_challan_ids = []
        
        # Store stats
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.skipped_messages = []
        
        # Store user choice
        self.should_replace = False
        self.existing_pdf_paths = []
        
        # Create UI (FAST - no complex widgets)
        self.create_widgets()
    
    def create_widgets(self):
        """Create main UI widgets - LIGHTWEIGHT"""
        
        main_frame = ctk.CTkFrame(self, fg_color="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        header = ctk.CTkLabel(
            main_frame,
            text=f"{self.total_challans} Challan(s) | {self.total_pages} Page(s) | 4 per page",
            font=("Arial", 18, "bold"),
            text_color="#1e3a5f"
        )
        header.pack(pady=20)
        
        summary_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10)
        summary_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        summary_text = ctk.CTkTextbox(
            summary_frame,
            height=200,
            font=("Courier New", 12),
            fg_color="white",
            state="normal"
        )
        summary_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        summary = self._generate_summary()
        summary_text.insert("1.0", summary)
        summary_text.configure(state="disabled")
        
        footer_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10)
        footer_frame.pack(fill="x", padx=20, pady=10)
        
        footer_label = ctk.CTkLabel(
            footer_frame,
            text="Footer Text (English):",
            font=("Arial", 13, "bold"),
            text_color="#1e3a5f"
        )
        footer_label.pack(pady=(10, 5))
        
        self.footer_text = ctk.CTkTextbox(
            footer_frame,
            height=50,
            font=("Arial", 12),
            fg_color="white",
            border_color="#bdc3c7",
            border_width=1
        )
        self.footer_text.pack(fill="x", padx=10, pady=5)
        
        self.footer_text.insert("1.0", "Please pay fees before the due date")
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        generate_btn = ctk.CTkButton(
            button_frame,
            text="Save & Generate PDF (4 per page)",
            font=("Arial", 13, "bold"),
            fg_color="#27ae60",
            hover_color="#229954",
            height=45,
            command=lambda: self.generate_pdf("4")
        )
        generate_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        generate_2_btn = ctk.CTkButton(
            button_frame,
            text="Save & Generate 2 per page",
            font=("Arial", 13, "bold"),
            fg_color="#2980b9",
            hover_color="#1e6fa8",
            height=45,
            command=lambda: self.generate_pdf("2")
        )
        generate_2_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        generate_1_btn = ctk.CTkButton(
            button_frame,
            text="Save & Generate 1 per page",
            font=("Arial", 13, "bold"),
            fg_color="#8e44ad",
            hover_color="#7d3c98",
            height=45,
            command=lambda: self.generate_pdf("1")
        )
        generate_1_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            font=("Arial", 13, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=100,
            height=45,
            command=self.destroy
        )
        close_btn.pack(side="right", padx=5)
    
    def _generate_summary(self) -> str:
        """Generate a simple text summary of challans"""
        summary = "=" * 80 + "\n"
        summary += "FEE CHALLAN PREVIEW SUMMARY\n"
        summary += "=" * 80 + "\n\n"
        summary += f"Total Challans: {self.total_challans}\n"
        summary += f"Total Pages: {self.total_pages}\n"
        summary += f"Challans per page: {self.challans_per_page}\n\n"
        summary += "-" * 80 + "\n"
        
        for i, challan_data in enumerate(self.challans_data, 1):
            family_id = challan_data.get('family_id', 'N/A')
            guardian_name = challan_data.get('guardian_name', 'N/A')
            month = challan_data.get('challan_month', 'N/A')
            year = challan_data.get('challan_year', 'N/A')
            due_date = challan_data.get('due_date', 'N/A')
            students = challan_data.get('students', [])
            
            total_monthly = challan_data.get('total_monthly_tuition_fee', 0)
            total_arrears = challan_data.get('total_arrears', 0)
            total_concession = challan_data.get('total_fee_concession', 0)
            admission_fee = challan_data.get('admission_fee', 0)
            registration_fee = challan_data.get('registration_fee', 0)
            exam_fee = challan_data.get('exam_fee', 0)
            transport_fee = challan_data.get('transport_fee', 0)
            other_fee = challan_data.get('other_fee', 0)
            
            total = (total_monthly + admission_fee + registration_fee + exam_fee + transport_fee + other_fee + total_arrears)
            amount_due = total - total_concession
            
            summary += f"Challan #{i}:\n"
            summary += f"  Family ID: {family_id}\n"
            summary += f"  Guardian: {guardian_name}\n"
            summary += f"  Month: {month} {year}\n"
            summary += f"  Due Date: {due_date}\n"
            summary += f"  Students ({len(students)}):\n"
            
            for student in students:
                summary += f"    - {student.first_name} {student.last_name} (ID: {student.student_id})\n"
                summary += f"      Class: {student.class_grade} | Fee: Rs. {student.monthly_tuition_fee:.0f} | Concession: Rs. {student.fee_concession:.0f}\n"
            
            summary += f"  Total Monthly: Rs. {total_monthly:.0f}\n"
            summary += f"  Arrears: Rs. {total_arrears:.0f}\n"
            summary += f"  Concession: Rs. {total_concession:.0f}\n"
            summary += f"  Total: Rs. {amount_due:.0f}\n"
            summary += f"  Amount Due: Rs. {amount_due:.0f}\n\n"
        
        summary += "=" * 80 + "\n"
        summary += "Footer Text:\n"
        summary += f"{self.footer_text.get('1.0', 'end-1c') if hasattr(self, 'footer_text') else 'Please pay fees before the due date'}\n"
        summary += "=" * 80 + "\n"
        
        return summary
    
    def create_database_challans(self):
        """Create challan records in database - ONE PER FAMILY with replace/keep logic"""
        try:
            if not self.challans_data:
                return
            
            self.created_count = 0
            self.updated_count = 0
            self.skipped_count = 0
            self.skipped_messages = []
            self.existing_pdf_paths = []
            
            # Check if ANY challans already exist
            existing_families = []
            new_families = []
            
            for challan_data in self.challans_data:
                family_id = challan_data.get('family_id')
                challan_month = challan_data.get('challan_month')
                challan_year = challan_data.get('challan_year', str(datetime.now().year))
                
                if not family_id:
                    self.skipped_count += 1
                    self.skipped_messages.append("Missing family_id")
                    continue
                
                # Check if challan exists
                exists = self.fee_service.check_challan_exists(family_id, challan_month, challan_year)
                
                if exists:
                    existing_families.append((challan_data, family_id, challan_month, challan_year))
                else:
                    new_families.append(challan_data)
            
            # Ask ONCE if there are existing challans
            self.should_replace = False
            if existing_families:
                self.should_replace = messagebox.askyesno(
                    "Challans Already Exist",
                    f"Challans already exist for {len(existing_families)} family/families for this month.\n\n"
                    f"Do you want to replace them?"
                )
            
            # Process existing families
            if existing_families:
                for challan_data, family_id, challan_month, challan_year in existing_families:
                    # Get the existing challan
                    existing_challan = self.db.query(FeeChallan).filter(
                        FeeChallan.family_id == family_id,
                        FeeChallan.challan_month == challan_month,
                        FeeChallan.challan_year == challan_year
                    ).first()
                    
                    if self.should_replace:
                        # UPDATE the existing challan with new data (keep same ID and Bill ID)
                        if existing_challan:
                            # Update fees
                            existing_challan.total_monthly_tuition_fee = challan_data.get('total_monthly_tuition_fee', existing_challan.total_monthly_tuition_fee)
                            existing_challan.total_admission_fee = challan_data.get('admission_fee', existing_challan.total_admission_fee)
                            existing_challan.total_registration_fee = challan_data.get('registration_fee', existing_challan.total_registration_fee)
                            existing_challan.total_exam_fee = challan_data.get('exam_fee', existing_challan.total_exam_fee)
                            existing_challan.total_transport_fee = challan_data.get('transport_fee', existing_challan.total_transport_fee)
                            existing_challan.total_other_fee = challan_data.get('other_fee', existing_challan.total_other_fee)
                            existing_challan.total_arrears = challan_data.get('total_arrears', existing_challan.total_arrears)
                            existing_challan.total_fee_concession = challan_data.get('total_fee_concession', existing_challan.total_fee_concession)
                            
                            # Calculate new totals
                            total_monthly = existing_challan.total_monthly_tuition_fee
                            total_concession = existing_challan.total_fee_concession
                            total_arrears = existing_challan.total_arrears
                            admission_fee = existing_challan.total_admission_fee
                            registration_fee = existing_challan.total_registration_fee
                            exam_fee = existing_challan.total_exam_fee
                            transport_fee = existing_challan.total_transport_fee
                            other_fee = existing_challan.total_other_fee
                            
                            total_amount = total_monthly + total_arrears + admission_fee + registration_fee + exam_fee + transport_fee + other_fee
                            amount_due = total_amount - total_concession
                            exact_payable = total_monthly + admission_fee + registration_fee + exam_fee + transport_fee + other_fee - total_concession
                            
                            existing_challan.total_amount = total_amount
                            existing_challan.amount_due = amount_due
                            existing_challan.exact_payable = exact_payable
                            existing_challan.remaining_amount = amount_due
                            
                            # Update due date
                            due_date_str = challan_data.get('due_date', date.today().strftime("%Y-%m-%d"))
                            try:
                                existing_challan.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                            except ValueError:
                                pass
                            
                            # Update guardian info
                            existing_challan.guardian_name = challan_data.get('guardian_name', existing_challan.guardian_name)
                            existing_challan.guardian_cnic = challan_data.get('guardian_cnic', existing_challan.guardian_cnic)
                            
                            # Save
                            self.db.commit()
                            
                            self.generated_challan_ids.append(existing_challan.id)
                            self.updated_count += 1
                            print(f"Updated existing challan: {existing_challan.bill_id}")
                        else:
                            self.skipped_count += 1
                            self.skipped_messages.append(f"Could not find existing challan for {family_id}")
                    else:
                        # User chose NOT to replace - use existing challan
                        if existing_challan:
                            self.generated_challan_ids.append(existing_challan.id)
                            print(f"Using existing challan: {existing_challan.bill_id}")
                        else:
                            self.skipped_count += 1
                            self.skipped_messages.append(f"Could not find existing challan for {family_id}")
            
            # Process new families (no existing challan)
            if new_families:
                for challan_data in new_families:
                    result = self.fee_service.create_challan(challan_data)
                    if result['success']:
                        self.generated_challan_ids.append(result['challan_id'])
                        self.created_count += 1
                        print(f"Created new challan: {result['bill_id']}")
                    else:
                        self.skipped_count += 1
                        self.skipped_messages.append(result['message'])
            
            # NO POPUP HERE - Just print to console
            print(f"Created: {self.created_count} | Updated: {self.updated_count} | Skipped: {self.skipped_count}")
            
        except Exception as e:
            print(f"Error creating challans: {str(e)}")
    
    def generate_pdf(self, mode="4"):
        """Generate PDF and save to challans directory"""
        try:
            # Call create_database_challans() HERE - when user clicks Generate PDF
            self.create_database_challans()
            
            if not self.generated_challan_ids:
                messagebox.showerror(
                    "Error",
                    "No challans available to generate PDF!\n\n"
                    "Please go back and select families to generate challans."
                )
                return
            
            footer_text = self.footer_text.get("1.0", "end-1c")
            
            if not footer_text.strip():
                messagebox.showwarning("Empty Footer", "Please enter footer text!")
                return
            
            from app.utils.challan_printer import ChallanPrinter
            
            printer = ChallanPrinter(self.db)
            
            # If replacing, find and overwrite the MOST RECENT PDF file
            if self.should_replace:
                # Get all PDF files in challans directory
                pdf_files = [f for f in os.listdir(self.challans_dir) if f.endswith('.pdf')]
                
                if pdf_files:
                    # Sort by modification time (oldest first)
                    pdf_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.challans_dir, f)))
                    
                    # Use the most recent file (overwrite it)
                    pdf_filename = pdf_files[-1]
                    print(f"Replacing existing PDF: {pdf_filename}")
                else:
                    # No existing files - create new
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    pdf_filename = f"Challans_Batch_{timestamp}.pdf"
            else:
                # Not replacing - create new file with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                pdf_filename = f"Challans_Batch_{timestamp}.pdf"
            
            try:
                pdf_path = printer.generate_multiple_challans_pdf(
                    self.generated_challan_ids,
                    challans_per_page=4,
                    filename=pdf_filename,
                    footer_text=footer_text,
                    mode=mode
                )
            except Exception as e:
                messagebox.showerror(
                    "PDF Generation Error",
                    f"Failed to generate PDF: {str(e)}\n\n"
                    f"Please check:\n"
                    f"1. ReportLab is installed correctly\n"
                    f"2. The challans directory is writable\n"
                    f"3. There's enough disk space"
                )
                return
            
            if pdf_path:
                try:
                    for challan_id in self.generated_challan_ids:
                        challan = self.db.query(FeeChallan).filter(FeeChallan.id == challan_id).first()
                        if challan:
                            challan.urdu_footer = footer_text
                            challan.status = "Printed"
                            challan.printed_date = date.today()
                    self.db.commit()
                except Exception as e:
                    print(f"Warning: Could not update challan status: {str(e)}")
                
                if mode == "2":
                    title = "2 Challans per Page"
                elif mode == "1":
                    title = "1 Challan per Page"
                else:
                    title = "4 Challans per Page"
                
                # Show ONLY this success message after PDF is generated
                success_msg = f"PDF generated successfully!\n\n"
                success_msg += f"Mode: {title}\n"
                success_msg += f"Challans: {len(self.generated_challan_ids)}\n"
                success_msg += f"Saved to: {pdf_path}\n\n"
                success_msg += f"You can now print this file!"
                
                if self.created_count > 0:
                    success_msg += f"\n\nCreated: {self.created_count} new challan(s)"
                if self.updated_count > 0:
                    success_msg += f"\nUpdated: {self.updated_count} existing challan(s)"
                if self.skipped_count > 0:
                    success_msg += f"\nSkipped: {self.skipped_count}"
                
                messagebox.showinfo("Success", success_msg)
                self.destroy()
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to generate PDF - No file was created.\n\n"
                    "Please try again or contact support."
                )
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to generate PDF: {str(e)}\n\n"
                f"Please try again or contact support if the issue persists."
            )