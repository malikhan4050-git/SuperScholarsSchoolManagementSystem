"""
ID Generator Utility for Super Scholars School Management System
"""

import random
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import Student, Guardian


class IDGenerator:
    """Generate unique IDs for students and families"""
    
    @staticmethod
    def generate_student_id(db: Session, class_grade: str = None) -> str:
        """
        Generate a unique student ID
        Format: SS-XXX
        Example: SS-001 (First student)
                 SS-002 (Second student)
                 SS-003 (Third student)
        
        Args:
            db: Database session
            class_grade: The class/grade of the student (e.g., "10", "5", "7")
                         Not used for ID generation anymore, but kept for compatibility
        """
        # Get all students to find the highest sequence number
        all_students = db.query(Student).all()
        
        # Find max sequence number
        max_seq = 0
        for student in all_students:
            # Check if student ID matches format SS-XXX
            if student.student_id.startswith("SS-"):
                try:
                    seq = int(student.student_id.split('-')[-1])
                    if seq > max_seq:
                        max_seq = seq
                except:
                    continue
        
        # Generate the new student ID
        next_seq = max_seq + 1
        new_id = f"SS-{next_seq:03d}"
        
        return new_id
    
    @staticmethod
    def generate_family_id(db: Session) -> str:
        """
        Generate a unique family ID
        Format: FMYY-X
        Example: FM26-1 (First family in 2026)
                 FM26-2 (Second family in 2026)
                 FM26-3 (Third family in 2026)
                 FM25-1 (First family in 2025)
        """
        year = datetime.now().year
        yy = str(year)[-2:]  # Get last 2 digits of year (e.g., "26" for 2026)
        
        # Get all guardians to find the highest sequence number for this year
        all_guardians = db.query(Guardian).all()
        
        # Find max sequence number for this year
        max_seq = 0
        for guardian in all_guardians:
            # Check if family ID matches format FMYY-X
            if guardian.family_id.startswith(f"FM{yy}-"):
                try:
                    seq = int(guardian.family_id.split('-')[-1])
                    if seq > max_seq:
                        max_seq = seq
                except:
                    continue
        
        # Generate the new family ID
        next_seq = max_seq + 1
        new_id = f"FM{yy}-{next_seq}"
        
        return new_id
    
    @staticmethod
    def generate_receipt_number() -> str:
        """
        Generate a unique receipt number
        Format: RCPT-YYYYMMDD-XXXXX
        """
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        random_num = random.randint(10000, 99999)
        
        return f"RCPT-{date_str}-{random_num}"
    
    @staticmethod
    def generate_bill_id(family_id: str, challan_month: str = "January", year: int = None) -> str:
        """
        Generate a unique bill ID linked to the FAMILY and selected month
        Format: FMYY-X-MMM
        Example: FM26-1-JAN (for January)
                 FM26-2-FEB (for February)
        
        Args:
            family_id: The family's registration ID (e.g., FM26-1)
            challan_month: The month name for which the challan is being generated (e.g., "January")
            year: The year for the bill (defaults to current year)
        """
        if year is None:
            year = datetime.now().year
        
        # Map month name to month abbreviation
        month_abbr_map = {
            "January": "JAN", "February": "FEB", "March": "MAR", "April": "APR",
            "May": "MAY", "June": "JUN", "July": "JUL", "August": "AUG",
            "September": "SEP", "October": "OCT", "November": "NOV", "December": "DEC"
        }
        
        # Get month abbreviation (default to JAN if invalid)
        month_abbr = month_abbr_map.get(challan_month, "JAN")
        
        # Generate bill ID with FAMILY ID and month abbreviation
        return f"{family_id}-{month_abbr}"