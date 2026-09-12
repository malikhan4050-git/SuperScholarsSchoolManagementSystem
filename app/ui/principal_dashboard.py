# """
# Principal Dashboard for Super Scholars School Management System
# """

# import customtkinter as ctk
# from tkinter import messagebox
# import sys
# import os
# from sqlalchemy import func
# from datetime import datetime

# # Add project root to path
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# from app.database.models import SessionLocal, Guardian, Student, FeeRecord, FeeStatus, Teacher, FeeChallan
# from app.utils.auth import Authentication
# from app.services.fee_service import FeeService

# class PrincipalDashboard(ctk.CTk):
#     """Principal Dashboard Class - View Only Access"""
    
#     def __init__(self, user):
#         super().__init__()
        
#         # Store current user
#         self.current_user = user
        
#         # Configure window
#         self.title("Super Scholars - Principal Dashboard")
#         self.geometry("1400x800")
        
#         # Set theme
#         ctk.set_appearance_mode("light")
#         ctk.set_default_color_theme("blue")
        
#         # Initialize database
#         self.db = SessionLocal()
#         self.auth = Authentication(self.db)
#         self.auth.current_user = user
#         self.fee_service = FeeService(self.db)
        
#         # Create UI
#         self.create_widgets()
        
#     def create_widgets(self):
#         """Create main dashboard layout"""
        
#         # Configure grid
#         self.grid_columnconfigure(1, weight=1)
#         self.grid_rowconfigure(0, weight=1)
        
#         # Create sidebar
#         self.create_sidebar()
        
#         # Create main content area
#         self.create_main_content()
        
#     def create_sidebar(self):
#         """Create sidebar navigation"""
        
#         self.sidebar = ctk.CTkFrame(
#             self,
#             width=250,
#             corner_radius=0,
#             fg_color="#1e3a5f"
#         )
#         self.sidebar.grid(row=0, column=0, sticky="nsew")
        
#         # Logo
#         self.logo_label = ctk.CTkLabel(
#             self.sidebar,
#             text="SUPER\nSCHOLARS",
#             font=("Arial", 20, "bold"),
#             text_color="white",
#             justify="center"
#         )
#         self.logo_label.pack(pady=(30, 40))
        
#         # User info frame
#         self.user_frame = ctk.CTkFrame(
#             self.sidebar,
#             fg_color="#2c5282",
#             corner_radius=10
#         )
#         self.user_frame.pack(padx=20, pady=(0, 30), fill="x")
        
#         self.user_name = ctk.CTkLabel(
#             self.user_frame,
#             text=f"{self.current_user.full_name}",
#             font=("Arial", 14, "bold"),
#             text_color="white"
#         )
#         self.user_name.pack(pady=10)
        
#         self.user_role = ctk.CTkLabel(
#             self.user_frame,
#             text="Principal",
#             font=("Arial", 12),
#             text_color="#a0b4c8"
#         )
#         self.user_role.pack(pady=(0, 10))
        
#         # Navigation buttons - Dashboard, Students, Fees, Reports
#         nav_items = [
#             ("Dashboard", self.show_dashboard),
#             ("Students", self.show_students),
#             ("Fees", self.show_fees),
#             ("Reports", self.show_reports)
#         ]
        
#         for text, command in nav_items:
#             button = ctk.CTkButton(
#                 self.sidebar,
#                 text=text,
#                 width=200,
#                 height=40,
#                 font=("Arial", 14),
#                 fg_color="transparent",
#                 hover_color="#2c5282",
#                 anchor="w",
#                 command=command
#             )
#             button.pack(padx=20, pady=5)
        
#         # Logout button
#         self.logout_button = ctk.CTkButton(
#             self.sidebar,
#             text="Logout",
#             width=200,
#             height=40,
#             font=("Arial", 14),
#             fg_color="#e74c3c",
#             hover_color="#c0392b",
#             command=self.logout
#         )
#         self.logout_button.pack(side="bottom", padx=20, pady=20)
        
#     def create_main_content(self):
#         """Create main content area"""
        
#         self.main_content = ctk.CTkFrame(
#             self,
#             corner_radius=0,
#             fg_color="#f0f2f5"
#         )
#         self.main_content.grid(row=0, column=1, sticky="nsew")
        
#         # Initialize with dashboard
#         self.show_dashboard()
        
#     def clear_main_content(self):
#         """Clear main content area"""
#         for widget in self.main_content.winfo_children():
#             widget.destroy()
    
#     def show_dashboard(self):
#         """Show dashboard view"""
#         self.clear_main_content()
        
#         # Header
#         self.header_frame = ctk.CTkFrame(
#             self.main_content,
#             height=100,
#             fg_color="white",
#             corner_radius=0
#         )
#         self.header_frame.pack(fill="x")
        
#         self.header_title = ctk.CTkLabel(
#             self.header_frame,
#             text="Dashboard Overview",
#             font=("Arial", 24, "bold"),
#             text_color="#1e3a5f"
#         )
#         self.header_title.pack(side="left", padx=30, pady=30)
        
#         # Stats cards
#         self.stats_frame = ctk.CTkFrame(
#             self.main_content,
#             fg_color="transparent"
#         )
#         self.stats_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
#         # Get actual stats
#         total_students = self.db.query(Student).count()
#         total_families = self.db.query(Guardian).count()
#         total_teachers = self.db.query(Teacher).count()
        
#         # FIXED: Calculate total collected from FeeChallan (not FeeRecord)
#         total_collected = self.db.query(FeeChallan).with_entities(
#             func.sum(FeeChallan.paid_amount)
#         ).scalar() or 0
        
#         # FIXED: Calculate total outstanding from FeeChallan
#         total_outstanding = self.db.query(FeeChallan).with_entities(
#             func.sum(FeeChallan.remaining_amount)
#         ).scalar() or 0
        
#         # FIXED: Count pending challans
#         pending_challans = self.db.query(FeeChallan).filter(
#             FeeChallan.is_paid == False
#         ).count()
        
#         stats = [
#             ("Total Students", total_students, "#3498db"),
#             ("Total Teachers", total_teachers, "#2ecc71"),
#             ("Total Families", total_families, "#e74c3c"),
#             ("Pending Challans", pending_challans, "#9b59b6"),
#             ("Total Collected", f"Rs. {total_collected:,.0f}", "#f39c12"),
#             ("Outstanding", f"Rs. {total_outstanding:,.0f}", "#e67e22")
#         ]
        
#         # Make 6 cards fit
#         for i in range(6):
#             self.stats_frame.grid_columnconfigure(i, weight=1)
        
#         for i, (title, value, color) in enumerate(stats):
#             card = ctk.CTkFrame(
#                 self.stats_frame,
#                 width=180,
#                 height=150,
#                 fg_color="white",
#                 corner_radius=15
#             )
#             card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            
#             value_label = ctk.CTkLabel(
#                 card,
#                 text=str(value),
#                 font=("Arial", 24, "bold"),
#                 text_color=color
#             )
#             value_label.pack(pady=(30, 5))
            
#             title_label = ctk.CTkLabel(
#                 card,
#                 text=title,
#                 font=("Arial", 14),
#                 text_color="gray"
#             )
#             title_label.pack(pady=(0, 30))
    
#     def show_students(self):
#         """Show students view (Read Only)"""
#         self.clear_main_content()
        
#         # Header
#         self.header_frame = ctk.CTkFrame(
#             self.main_content,
#             height=100,
#             fg_color="white",
#             corner_radius=0
#         )
#         self.header_frame.pack(fill="x")
        
#         self.header_title = ctk.CTkLabel(
#             self.header_frame,
#             text="Student Management (View Only)",
#             font=("Arial", 24, "bold"),
#             text_color="#1e3a5f"
#         )
#         self.header_title.pack(side="left", padx=30, pady=30)
        
#         # Students list frame
#         self.students_frame = ctk.CTkFrame(
#             self.main_content,
#             fg_color="white",
#             corner_radius=10
#         )
#         self.students_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
#         # Refresh students list
#         self.refresh_students_list()
    
#     def refresh_students_list(self):
#         """Refresh the students list"""
#         for widget in self.students_frame.winfo_children():
#             widget.destroy()
        
#         # Title
#         list_title = ctk.CTkLabel(
#             self.students_frame,
#             text="All Students",
#             font=("Arial", 18, "bold"),
#             text_color="#1e3a5f"
#         )
#         list_title.pack(pady=10)
        
#         # Get all students
#         students = self.db.query(Student).all()
        
#         if not students:
#             empty_label = ctk.CTkLabel(
#                 self.students_frame,
#                 text="No students found.",
#                 font=("Arial", 14),
#                 text_color="gray"
#             )
#             empty_label.pack(pady=50)
#             return
        
#         # Create scrollable frame for students
#         scroll_frame = ctk.CTkScrollableFrame(
#             self.students_frame,
#             fg_color="transparent"
#         )
#         scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
#         # Student cards
#         for student in students:
#             student_card = ctk.CTkFrame(
#                 scroll_frame,
#                 fg_color="#f8f9fa",
#                 corner_radius=8
#             )
#             student_card.pack(fill="x", padx=10, pady=5)
            
#             # Get guardian for this student
#             guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
#             family_id = guardian.family_id if guardian else "N/A"
            
#             # Student info with family ID
#             info_text = f"{student.full_name} | ID: {student.student_id} | Family: {family_id} | Class: {student.class_grade} | Fee: Rs. {student.monthly_tuition_fee:,.0f}"
            
#             student_label = ctk.CTkLabel(
#                 student_card,
#                 text=info_text,
#                 font=("Arial", 13),
#                 text_color="#2c3e50"
#             )
#             student_label.pack(side="left", padx=15, pady=10)
            
#             # View button (Read Only)
#             view_btn = ctk.CTkButton(
#                 student_card,
#                 text="View",
#                 width=80,
#                 height=30,
#                 fg_color="#3498db",
#                 hover_color="#2980b9",
#                 command=lambda sid=student.id: self.view_student(sid)
#             )
#             view_btn.pack(side="right", padx=5, pady=5)
    
#     def view_student(self, student_id):
#         """View student details (Read Only - Opens Full Details Window)"""
#         from app.ui.student_details_screen import StudentDetailsWindow
#         StudentDetailsWindow(self, student_id, self.db)
    
#     def show_fees(self):
#         """Show fees view (View Only)"""
#         self.clear_main_content()
        
#         # Header
#         self.header_frame = ctk.CTkFrame(
#             self.main_content,
#             height=100,
#             fg_color="white",
#             corner_radius=0
#         )
#         self.header_frame.pack(fill="x")
        
#         self.header_title = ctk.CTkLabel(
#             self.header_frame,
#             text="Fee Management (View Only)",
#             font=("Arial", 24, "bold"),
#             text_color="#1e3a5f"
#         )
#         self.header_title.pack(side="left", padx=30, pady=30)
        
#         # Fee summary
#         summary_frame = ctk.CTkFrame(
#             self.main_content,
#             fg_color="white",
#             corner_radius=10
#         )
#         summary_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
#         # Calculate from FeeChallan (correct)
#         total_billed = self.db.query(FeeChallan).with_entities(
#             func.sum(FeeChallan.total_amount)
#         ).scalar() or 0
        
#         total_collected = self.db.query(FeeChallan).with_entities(
#             func.sum(FeeChallan.paid_amount)
#         ).scalar() or 0
        
#         total_outstanding = self.db.query(FeeChallan).with_entities(
#             func.sum(FeeChallan.remaining_amount)
#         ).scalar() or 0
        
#         # Display summary
#         summary_text = f"""
#         Fee Summary:
#         ============
#         Total Billed:        Rs. {total_billed:,.0f}
#         Total Collected:     Rs. {total_collected:,.0f}
#         Total Outstanding:   Rs. {total_outstanding:,.0f}
#         """
        
#         summary_label = ctk.CTkLabel(
#             summary_frame,
#             text=summary_text,
#             font=("Arial", 18),
#             text_color="#1e3a5f",
#             justify="left"
#         )
#         summary_label.pack(pady=50)
        
#         # View Challans button (Read Only)
#         view_challans_btn = ctk.CTkButton(
#             summary_frame,
#             text="View All Challans",
#             font=("Arial", 14, "bold"),
#             fg_color="#3498db",
#             hover_color="#2980b9",
#             width=200,
#             height=45,
#             command=self.view_all_challans
#         )
#         view_challans_btn.pack(pady=20)
        
#         # Note
#         note_label = ctk.CTkLabel(
#             summary_frame,
#             text="🔒 View Only - Contact Admin for fee management actions",
#             font=("Arial", 14),
#             text_color="gray"
#         )
#         note_label.pack(pady=10)
    
#     def view_all_challans(self):
#         """View all challans (Read Only)"""
        
#         # Get all challans
#         challans = self.db.query(FeeChallan).order_by(FeeChallan.created_at.desc()).all()
        
#         if not challans:
#             messagebox.showinfo("No Challans", "No challans found!")
#             return
        
#         # Create a new window to show challans
#         challan_window = ctk.CTkToplevel(self)
#         challan_window.title("All Fee Challans (View Only)")
#         challan_window.geometry("1000x600")
        
#         # Create scrollable frame
#         scroll_frame = ctk.CTkScrollableFrame(challan_window, fg_color="white")
#         scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
#         # Title
#         title_label = ctk.CTkLabel(
#             scroll_frame,
#             text=f"All Fee Challans ({len(challans)})",
#             font=("Arial", 20, "bold"),
#             text_color="#1e3a5f"
#         )
#         title_label.pack(pady=10)
        
#         # Show each challan
#         for challan in challans:
#             # Get guardian for this challan
#             guardian = self.db.query(Guardian).filter(Guardian.family_id == challan.family_id).first()
#             guardian_name = guardian.guardian_name if guardian else "N/A"
            
#             # Determine status color
#             if challan.is_paid:
#                 status = "PAID"
#                 status_color = "#2ecc71"
#             elif challan.paid_amount > 0:
#                 status = "PARTIAL"
#                 status_color = "#f39c12"
#             else:
#                 status = "UNPAID"
#                 status_color = "#e74c3c"
            
#             # Create challan card
#             challan_card = ctk.CTkFrame(
#                 scroll_frame,
#                 fg_color="#f8f9fa",
#                 corner_radius=8
#             )
#             challan_card.pack(fill="x", padx=10, pady=5)
            
#             info_text = (
#                 f"Bill ID: {challan.bill_id} | Family: {challan.family_id} | "
#                 f"Guardian: {guardian_name} | Month: {challan.challan_month} {challan.challan_year} | "
#                 f"Amount: Rs. {challan.amount_due:,.0f} | "
#                 f"Paid: Rs. {challan.paid_amount:,.0f} | "
#                 f"Remaining: Rs. {challan.remaining_amount:,.0f} | "
#                 f"Status: {status}"
#             )
            
#             challan_label = ctk.CTkLabel(
#                 challan_card,
#                 text=info_text,
#                 font=("Arial", 12),
#                 text_color="#2c3e50",
#                 anchor="w"
#             )
#             challan_label.pack(side="left", padx=15, pady=10)
            
#             # Status badge
#             status_label = ctk.CTkLabel(
#                 challan_card,
#                 text=status,
#                 font=("Arial", 12, "bold"),
#                 text_color=status_color
#             )
#             status_label.pack(side="right", padx=15, pady=10)
    
#     def show_reports(self):
#         """Show reports view (View Only)"""
#         self.clear_main_content()
        
#         # Header
#         self.header_frame = ctk.CTkFrame(
#             self.main_content,
#             height=100,
#             fg_color="white",
#             corner_radius=0
#         )
#         self.header_frame.pack(fill="x")
        
#         self.header_title = ctk.CTkLabel(
#             self.header_frame,
#             text="Reports & Analytics",
#             font=("Arial", 24, "bold"),
#             text_color="#1e3a5f"
#         )
#         self.header_title.pack(side="left", padx=30, pady=30)
        
#         # Reports Content Frame
#         reports_frame = ctk.CTkFrame(
#             self.main_content,
#             fg_color="white",
#             corner_radius=10
#         )
#         reports_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
#         # Report Cards
#         self.create_report_card(reports_frame, "Fee Collection Summary", 
#             "View total billed, collected, and outstanding fees", 0, 0,
#             self.view_fee_collection_report)
        
#         self.create_report_card(reports_frame, "Outstanding Fees Report", 
#             "View all families with unpaid challans", 0, 1,
#             self.view_outstanding_report)
        
#         self.create_report_card(reports_frame, "All Challans Report", 
#             "View all generated fee challans", 1, 0,
#             self.view_all_challans)
        
#         self.create_report_card(reports_frame, "Student Enrollment Report", 
#             "View all students with their class and fee info", 1, 1,
#             self.view_student_enrollment_report)
        
#         # Note
#         note_label = ctk.CTkLabel(
#             reports_frame,
#             text="🔒 View Only Reports - Export functionality available to Admin only",
#             font=("Arial", 14),
#             text_color="gray"
#         )
#         note_label.grid(row=2, column=0, columnspan=2, pady=20)
    
#     def create_report_card(self, parent, title, description, row, col, command=None):
#         """Create a report card in grid layout"""
        
#         card = ctk.CTkFrame(
#             parent,
#             fg_color="#f8f9fa",
#             corner_radius=10,
#             border_width=1,
#             border_color="#e0e0e0"
#         )
#         card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
#         parent.grid_columnconfigure(col, weight=1)
#         parent.grid_rowconfigure(row, weight=1)
        
#         # Card Title
#         title_label = ctk.CTkLabel(
#             card,
#             text=title,
#             font=("Arial", 18, "bold"),
#             text_color="#1e3a5f"
#         )
#         title_label.pack(pady=(20, 10))
        
#         # Card Description
#         desc_label = ctk.CTkLabel(
#             card,
#             text=description,
#             font=("Arial", 14),
#             text_color="gray",
#             wraplength=300
#         )
#         desc_label.pack(pady=10)
        
#         # View Button
#         if command:
#             view_btn = ctk.CTkButton(
#                 card,
#                 text="View Report",
#                 font=("Arial", 13, "bold"),
#                 fg_color="#3498db",
#                 hover_color="#2980b9",
#                 width=150,
#                 height=40,
#                 command=command
#             )
#         else:
#             view_btn = ctk.CTkButton(
#                 card,
#                 text="View Report",
#                 font=("Arial", 13, "bold"),
#                 fg_color="#3498db",
#                 hover_color="#2980b9",
#                 width=150,
#                 height=40,
#                 state="disabled"
#             )
#         view_btn.pack(pady=20)
    
#     def view_fee_collection_report(self):
#         """View Fee Collection Summary Report"""
        
#         # Calculate totals
#         total_billed = self.db.query(FeeChallan).with_entities(
#             func.sum(FeeChallan.total_amount)
#         ).scalar() or 0
        
#         total_collected = self.db.query(FeeChallan).with_entities(
#             func.sum(FeeChallan.paid_amount)
#         ).scalar() or 0
        
#         total_outstanding = self.db.query(FeeChallan).with_entities(
#             func.sum(FeeChallan.remaining_amount)
#         ).scalar() or 0
        
#         # Create report window
#         report_window = ctk.CTkToplevel(self)
#         report_window.title("Fee Collection Report")
#         report_window.geometry("600x400")
        
#         report_frame = ctk.CTkFrame(report_window, fg_color="white", corner_radius=10)
#         report_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
#         report_text = f"""
#         FEE COLLECTION REPORT
#         =====================
        
#         Total Billed:        Rs. {total_billed:,.0f}
#         Total Collected:     Rs. {total_collected:,.0f}
#         Total Outstanding:   Rs. {total_outstanding:,.0f}
        
#         Collection Rate:     {((total_collected / total_billed) * 100):.1f}% (if total_billed > 0)
        
#         =====================
#         Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#         """
        
#         report_label = ctk.CTkLabel(
#             report_frame,
#             text=report_text,
#             font=("Arial", 16),
#             text_color="#1e3a5f",
#             justify="left"
#         )
#         report_label.pack(pady=50)
    
#     def view_outstanding_report(self):
#         """View Outstanding Fees Report"""
        
#         # Get all challans with remaining > 0
#         challans = self.db.query(FeeChallan).filter(FeeChallan.remaining_amount > 0).all()
        
#         if not challans:
#             messagebox.showinfo("No Outstanding Fees", "No outstanding fees found!")
#             return
        
#         # Create report window
#         report_window = ctk.CTkToplevel(self)
#         report_window.title("Outstanding Fees Report")
#         report_window.geometry("900x600")
        
#         # Create scrollable frame
#         scroll_frame = ctk.CTkScrollableFrame(report_window, fg_color="white")
#         scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
#         # Title
#         title_label = ctk.CTkLabel(
#             scroll_frame,
#             text=f"Outstanding Fees ({len(challans)} challans)",
#             font=("Arial", 20, "bold"),
#             text_color="#1e3a5f"
#         )
#         title_label.pack(pady=10)
        
#         # Show each outstanding challan
#         for challan in challans:
#             guardian = self.db.query(Guardian).filter(Guardian.family_id == challan.family_id).first()
#             guardian_name = guardian.guardian_name if guardian else "N/A"
            
#             challan_card = ctk.CTkFrame(
#                 scroll_frame,
#                 fg_color="#fdecea",
#                 corner_radius=8
#             )
#             challan_card.pack(fill="x", padx=10, pady=5)
            
#             info_text = (
#                 f"Bill ID: {challan.bill_id} | Family: {challan.family_id} | "
#                 f"Guardian: {guardian_name} | Month: {challan.challan_month} {challan.challan_year} | "
#                 f"Outstanding: Rs. {challan.remaining_amount:,.0f}"
#             )
            
#             challan_label = ctk.CTkLabel(
#                 challan_card,
#                 text=info_text,
#                 font=("Arial", 13),
#                 text_color="#e74c3c",
#                 anchor="w"
#             )
#             challan_label.pack(side="left", padx=15, pady=10)
    
#     def view_student_enrollment_report(self):
#         """View Student Enrollment Report"""
        
#         # Get all students
#         students = self.db.query(Student).all()
        
#         if not students:
#             messagebox.showinfo("No Students", "No students found!")
#             return
        
#         # Create report window
#         report_window = ctk.CTkToplevel(self)
#         report_window.title("Student Enrollment Report")
#         report_window.geometry("900x600")
        
#         # Create scrollable frame
#         scroll_frame = ctk.CTkScrollableFrame(report_window, fg_color="white")
#         scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
#         # Title
#         title_label = ctk.CTkLabel(
#             scroll_frame,
#             text=f"Student Enrollment ({len(students)} students)",
#             font=("Arial", 20, "bold"),
#             text_color="#1e3a5f"
#         )
#         title_label.pack(pady=10)
        
#         # Show each student
#         for student in students:
#             guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
#             family_id = guardian.family_id if guardian else "N/A"
            
#             student_card = ctk.CTkFrame(
#                 scroll_frame,
#                 fg_color="#f8f9fa",
#                 corner_radius=8
#             )
#             student_card.pack(fill="x", padx=10, pady=5)
            
#             info_text = (
#                 f"{student.full_name} | ID: {student.student_id} | "
#                 f"Family: {family_id} | Class: {student.class_grade} | "
#                 f"Fee: Rs. {student.monthly_tuition_fee:,.0f} | "
#                 f"Concession: Rs. {student.fee_concession:,.0f}"
#             )
            
#             student_label = ctk.CTkLabel(
#                 student_card,
#                 text=info_text,
#                 font=("Arial", 13),
#                 text_color="#2c3e50",
#                 anchor="w"
#             )
#             student_label.pack(side="left", padx=15, pady=10)
    
#     def logout(self):
#         """Logout from the system"""
#         if messagebox.askyesno("Confirm", "Are you sure you want to logout?"):
#             self.auth.logout()
#             self.db.close()
#             self.destroy()
            
#             # Import and show login window
#             from app.ui.login_window import LoginWindow
#             login_window = LoginWindow()
#             login_window.mainloop()

# if __name__ == "__main__":
#     # Test with a dummy user
#     from app.database.models import SessionLocal, User, UserRole
#     db = SessionLocal()
#     user = db.query(User).filter(User.role == UserRole.PRINCIPAL).first()
#     db.close()
    
#     if user:
#         app = PrincipalDashboard(user)
#         app.mainloop()