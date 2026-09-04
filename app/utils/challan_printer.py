"""
Challan Printer - PDF Generation using canvas with proper cells
"""

from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import SessionLocal, Student, Guardian, FeeChallan

# ReportLab imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm, cm
from reportlab.lib import colors


class ChallanPrinter:
    """Handle PDF generation using canvas with proper cells"""
    
    def __init__(self, db: Session = None):
        self.db = db if db else SessionLocal()
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "challans"
        )
        Path(self.output_dir).mkdir(exist_ok=True)
    
    def generate_multiple_challans_pdf(self, challan_ids: list, challans_per_page: int = 4, filename: str = None, footer_text: str = None, mode: str = "4") -> str:
        """Generate PDF with different modes:
        - mode="4": 4 challans per page (1 copy each, no labels)
        - mode="2": 2 challans per page, each with 2 copies (Parents + School)
        - mode="1": 1 challan per page, 3 copies (Parents + Bank + School)
        """
        
        if not filename:
            filename = f"Challans_Batch_{date.today().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Get all challans in ONE query
        all_challans = self.db.query(FeeChallan).filter(FeeChallan.id.in_(challan_ids)).all()
        challan_map = {c.id: c for c in all_challans}
        
        # Create canvas
        c = canvas.Canvas(filepath, pagesize=landscape(A4))
        page_width, page_height = landscape(A4)  # 842 x 595
        
        # Set margins
        margin = 10
        
        # Process based on mode
        if mode == "2":
            self._generate_2_per_page(c, challan_ids, challan_map, footer_text, page_width, page_height, margin)
        elif mode == "1":
            self._generate_1_per_page(c, challan_ids, challan_map, footer_text, page_width, page_height, margin)
        else:
            self._generate_4_per_page(c, challan_ids, challan_map, footer_text, page_width, page_height, margin)
        
        # Save PDF
        c.save()
        
        return filepath
    
    def _get_challan_data(self, challan):
        """Get guardian and students for a challan"""
        guardian = self.db.query(Guardian).filter(Guardian.family_id == challan.family_id).first()
        students = []
        if guardian:
            students = self.db.query(Student).filter(Student.guardian_id == guardian.id).all()
        return guardian, students
    
    def _generate_4_per_page(self, c, challan_ids, challan_map, footer_text, page_width, page_height, margin):
        """Generate 4 challans per page (1 copy each - no labels)"""
        
        challan_width = (page_width - 5 * margin) / 4
        challan_height = page_height - 2 * margin - 50
        
        for idx, challan_id in enumerate(challan_ids):
            challan = challan_map.get(challan_id)
            if not challan:
                continue
            
            guardian, students = self._get_challan_data(challan)
            
            page_idx = idx // 4
            col_idx = idx % 4
            
            if col_idx == 0 and page_idx > 0:
                c.showPage()
            
            x = margin + col_idx * (challan_width + margin)
            y = margin + 25
            
            self._draw_challan(c, x, y, challan_width, challan_height, challan, guardian, students, footer_text, "")
    
    def _generate_2_per_page(self, c, challan_ids, challan_map, footer_text, page_width, page_height, margin):
        """Generate 2 challans per page, each with 2 copies (Parents + School)"""
        
        challan_width = (page_width - 5 * margin) / 4
        challan_height = page_height - 2 * margin - 50
        
        # Process challans in pairs (2 challans per page)
        for i in range(0, len(challan_ids), 2):
            batch = challan_ids[i:i+2]
            
            # Get challan data for both challans
            challans_data = []
            for challan_id in batch:
                challan = challan_map.get(challan_id)
                if not challan:
                    continue
                
                guardian, students = self._get_challan_data(challan)
                
                if guardian:
                    challans_data.append((challan, guardian, students))
            
            # Start new page for each pair
            if i > 0:
                c.showPage()
            
            # Layout: Challan A (2 copies) then Challan B (2 copies)
            positions = [
                (margin, margin + 25),                                                    # Col 1
                (margin + challan_width + margin, margin + 25),                            # Col 2
                (margin + 2 * (challan_width + margin), margin + 25),                      # Col 3
                (margin + 3 * (challan_width + margin), margin + 25),                      # Col 4
            ]
            
            # Draw challans
            if len(challans_data) >= 1:
                # Challan A - Parents Copy (Col 1)
                self._draw_challan(c, positions[0][0], positions[0][1], challan_width, challan_height, challans_data[0][0], challans_data[0][1], challans_data[0][2], footer_text, "PARENTS COPY")
                # Challan A - School Copy (Col 2)
                self._draw_challan(c, positions[1][0], positions[1][1], challan_width, challan_height, challans_data[0][0], challans_data[0][1], challans_data[0][2], footer_text, "SCHOOL COPY")
            
            if len(challans_data) >= 2:
                # Challan B - Parents Copy (Col 3)
                self._draw_challan(c, positions[2][0], positions[2][1], challan_width, challan_height, challans_data[1][0], challans_data[1][1], challans_data[1][2], footer_text, "PARENTS COPY")
                # Challan B - School Copy (Col 4)
                self._draw_challan(c, positions[3][0], positions[3][1], challan_width, challan_height, challans_data[1][0], challans_data[1][1], challans_data[1][2], footer_text, "SCHOOL COPY")
    
    def _generate_1_per_page(self, c, challan_ids, challan_map, footer_text, page_width, page_height, margin):
        """Generate 1 challan per page, 3 copies (Parents + Bank + School)"""
        
        challan_width = (page_width - 5 * margin) / 4
        challan_height = page_height - 2 * margin - 50
        
        # Process each challan - 3 copies per challan
        for idx, challan_id in enumerate(challan_ids):
            challan = challan_map.get(challan_id)
            if not challan:
                continue
            
            guardian, students = self._get_challan_data(challan)
            
            # Start a new page for EACH challan (even first one)
            if idx > 0:
                c.showPage()
            
            # Layout: 3 copies of same challan on ONE page
            positions = [
                (margin, margin + 25),                                                    # Col 1
                (margin + challan_width + margin, margin + 25),                            # Col 2
                (margin + 2 * (challan_width + margin), margin + 25),                      # Col 3
            ]
            
            # Copy types
            copy_types = [
                "PARENTS COPY",
                "BANK COPY",
                "SCHOOL COPY",
            ]
            
            # Draw 3 copies of the same challan
            for j, copy_type in enumerate(copy_types):
                if j < 3:
                    self._draw_challan(c, positions[j][0], positions[j][1], challan_width, challan_height, challan, guardian, students, footer_text, copy_type)
        
    def _draw_challan(self, c, x, y, w, h, challan, guardian, students, footer_text=None, copy_type=""):
        """Draw a single challan with all students in the family - ALL TEXT CENTERED"""
        
        # Calculate totals from challan
        total_monthly = challan.total_monthly_tuition_fee if hasattr(challan, 'total_monthly_tuition_fee') else 0
        total_arrears = challan.total_arrears if hasattr(challan, 'total_arrears') else 0
        total_concession = challan.total_fee_concession if hasattr(challan, 'total_fee_concession') else 0
        admission_fee = challan.total_admission_fee if hasattr(challan, 'total_admission_fee') else 0
        registration_fee = challan.total_registration_fee if hasattr(challan, 'total_registration_fee') else 0
        exam_fee = challan.total_exam_fee if hasattr(challan, 'total_exam_fee') else 0
        transport_fee = challan.total_transport_fee if hasattr(challan, 'total_transport_fee') else 0
        other_fee = challan.total_other_fee if hasattr(challan, 'total_other_fee') else 0
        
        # Get the challan year
        challan_year = challan.challan_year if hasattr(challan, 'challan_year') else str(datetime.now().year)
        
        # Get the due date from the challan record
        due_date = challan.due_date if hasattr(challan, 'due_date') and challan.due_date else date.today()
        due_date_str = due_date.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
        
        # Calculate total (BEFORE concession)
        total_before_concession = total_monthly + total_arrears + admission_fee + registration_fee + exam_fee + transport_fee + other_fee
        
        # Calculate total (AFTER concession) - This is the PAYABLE BEFORE
        total_after_concession = total_before_concession - total_concession
        
        # PAYABLE AFTER = PAYABLE BEFORE + Late Fee (Rs. 100)
        payable_after = total_after_concession + 100
        
        # Set font sizes
        header_font_size = 7
        title_font_size = 9
        info_font_size = 6
        table_font_size = 6
        footer_font_size = 7
        
        # Draw main border
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.rect(x, y, w, h)
        
        # Draw copy type (if provided)
        if copy_type:
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(colors.HexColor('#e74c3c'))
            c.drawCentredString(x + w/2, y + h - 12, copy_type.upper())
        
        # ===== SCHOOL HEADER (Centered) =====
        c.setFillColor(colors.HexColor('#1e3a5f'))
        c.setFont("Helvetica-Bold", header_font_size)
        c.drawCentredString(x + w/2, y + h - 28, "THE SUPER")
        c.drawCentredString(x + w/2, y + h - 38, "SCHOLARS SCHOOL")
        
        c.setFont("Helvetica", info_font_size)
        c.setFillColor(colors.HexColor('#333333'))
        c.drawCentredString(x + w/2, y + h - 48, "Shamsabad Campus")
        c.drawCentredString(x + w/2, y + h - 56, "Tel: 057-2542710")
        
        # ===== TITLE (Centered) =====
        c.setFont("Helvetica-Bold", title_font_size)
        c.setFillColor(colors.HexColor('#1e3a5f'))
        c.drawCentredString(x + w/2, y + h - 75, "FEE CHALLAN")
        
        c.setFont("Helvetica", info_font_size)
        c.setFillColor(colors.HexColor('#333333'))
        c.drawCentredString(x + w/2, y + h - 84, "Deposit at School Office")
        
        # ===== STUDENT INFORMATION (Centered, New Layout) =====
        info_y = y + h - 110
        
        # List ALL students in the family with their classes
        if students:
            c.setFont("Helvetica-Bold", info_font_size)
            c.setFillColor(colors.HexColor('#333333'))
            
            # Show each student's name and class on SAME line for compactness
            for student in students:
                student_info = f"{student.first_name} {student.last_name} - Class {student.class_grade}"
                c.drawCentredString(x + w/2, info_y, f"Student: {student_info}")
                info_y -= 12  # Reduced spacing to fit more students
        else:
            c.setFont("Helvetica-Bold", info_font_size)
            c.setFillColor(colors.HexColor('#333333'))
            c.drawCentredString(x + w/2, info_y, "Student: N/A")
            info_y -= 12
        
        # Father Name
        c.setFont("Helvetica-Bold", info_font_size)
        c.drawCentredString(x + w/2, info_y, f"Father Name: {guardian.guardian_name if guardian else 'N/A'}")
        info_y -= 12
        
        # Fee Month and Year
        c.setFont("Helvetica", info_font_size)
        c.drawCentredString(x + w/2, info_y, f"Fee Month: {challan.challan_month} {challan_year}")
        info_y -= 12
        
        # Bill ID
        c.drawCentredString(x + w/2, info_y, f"Bill ID: {challan.bill_id}")
        
        # ===== FEE BREAKDOWN TABLE (Centered headers and data) =====
        table_top = info_y - 20
        
        # Table headers
        col1_left = x + 2
        col2_left = x + w/2 + 2
        col2_right = x + w - 2
        
        # Draw header cells
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.3)
        
        # Header row
        c.rect(col1_left, table_top - 10, col2_left - col1_left, 10)
        c.rect(col2_left, table_top - 10, col2_right - col2_left, 10)
        
        c.setFillColor(colors.HexColor('#333333'))
        c.setFont("Helvetica-Bold", table_font_size)
        
        # Center the header text within each cell
        c.drawCentredString(col1_left + (col2_left - col1_left)/2, table_top - 7, "Particulars")
        c.drawCentredString(col2_left + (col2_right - col2_left)/2, table_top - 7, "Amount (Rs.)")
        
        # Draw fee rows (ALL fee types)
        fees = [
            ("Tuition Fee", total_monthly),
            ("Registration Fee", registration_fee),
            ("Exam Fee", exam_fee),
            ("Admission Fee", admission_fee),
            ("Transport Fee", transport_fee),
            ("Arrears", total_arrears),
            ("Others", other_fee),
        ]
        
        row_y = table_top - 20
        row_height = 8
        
        for particular, amount in fees:
            # Draw cells for this row
            c.setStrokeColor(colors.grey)
            c.setLineWidth(0.3)
            c.rect(col1_left, row_y, col2_left - col1_left, row_height)
            c.rect(col2_left, row_y, col2_right - col2_left, row_height)
            
            # Draw text CENTERED within each cell
            c.setFillColor(colors.black)
            c.setFont("Helvetica", table_font_size)
            c.drawCentredString(col1_left + (col2_left - col1_left)/2, row_y + 2, particular)
            c.drawCentredString(col2_left + (col2_right - col2_left)/2, row_y + 2, f"{amount:.0f}")
            
            row_y -= row_height
        
        # ===== ADD GAP/SPACE BETWEEN FEE TABLE AND TOTAL TABLE =====
        row_y -= 15  # Add 15 units of empty space (NO separator line)
        
        # ===== TABLE 1: TOTAL + CONCESSION =====
        # TOTAL ROW (BEFORE CONCESSION)
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.3)
        c.rect(col1_left, row_y, col2_left - col1_left, row_height)
        c.rect(col2_left, row_y, col2_right - col2_left, row_height)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", table_font_size)
        c.drawCentredString(col1_left + (col2_left - col1_left)/2, row_y + 2, "Total")
        c.drawCentredString(col2_left + (col2_right - col2_left)/2, row_y + 2, f"{total_before_concession:.0f}")
        
        row_y -= row_height
        
        # CONCESSION ROW
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.3)
        c.rect(col1_left, row_y, col2_left - col1_left, row_height)
        c.rect(col2_left, row_y, col2_right - col2_left, row_height)
        
        c.setFont("Helvetica", table_font_size)
        c.drawCentredString(col1_left + (col2_left - col1_left)/2, row_y + 2, "Concession")
        c.drawCentredString(col2_left + (col2_right - col2_left)/2, row_y + 2, f"-{total_concession:.0f}")
        
        row_y -= row_height
        
        # ===== ADD GAP BETWEEN TABLE 1 AND TABLE 2 =====
        row_y -= 15  # Add 15 units of empty space
        
        # ===== TABLE 2: PAYABLE BEFORE + PAYABLE AFTER =====
        # PAYABLE BEFORE (Total after concession) - Using DUE DATE
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.3)
        c.rect(col1_left, row_y, col2_left - col1_left, row_height)
        c.rect(col2_left, row_y, col2_right - col2_left, row_height)
        
        c.setFont("Helvetica-Bold", table_font_size)
        c.drawCentredString(col1_left + (col2_left - col1_left)/2, row_y + 2, f"Payable Before {due_date_str}:")
        c.drawCentredString(col2_left + (col2_right - col2_left)/2, row_y + 2, f"{total_after_concession:.0f}")
        
        row_y -= row_height
        
        # PAYABLE AFTER (Total after concession + late fee) - Using DUE DATE
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.3)
        c.rect(col1_left, row_y, col2_left - col1_left, row_height)
        c.rect(col2_left, row_y, col2_right - col2_left, row_height)
        
        c.drawCentredString(col1_left + (col2_left - col1_left)/2, row_y + 2, f"Payable After {due_date_str}:")
        c.drawCentredString(col2_left + (col2_right - col2_left)/2, row_y + 2, f"{payable_after:.0f}")
        
        # ===== FOOTER (Centered in empty space between table and signatures) =====
        table_bottom = row_y - 10
        signature_y = y + 25
        footer_center_y = (table_bottom + signature_y) / 2
        
        # Use English text if provided, else default
        footer_text_to_use = footer_text if footer_text else "Please pay fees before the due date"
        
        # Simple wrapping: split by spaces, max 3 lines
        max_chars_per_line = 35
        words = footer_text_to_use.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars_per_line:
                current_line = current_line + " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw each line centered
        c.setFont("Helvetica-Bold", footer_font_size)
        c.setFillColor(colors.HexColor('#333333'))
        
        line_spacing = 14
        total_lines_height = len(lines) * line_spacing
        first_line_y = footer_center_y + (total_lines_height - line_spacing) / 2
        
        for i, line in enumerate(lines):
            line_y = first_line_y - i * line_spacing
            c.drawCentredString(x + w/2, line_y, line)
        
        # ===== SIGNATURES (At the bottom, Centered) =====
        c.setFont("Helvetica", footer_font_size)
        c.setFillColor(colors.HexColor('#333333'))
        c.drawCentredString(x + w/4, y + 15, "School Office Signature")
        c.drawCentredString(x + (3 * w / 4), y + 15, "School Office Stamp")