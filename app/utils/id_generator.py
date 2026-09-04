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
        Format: SS{class}-XXX
        Example: SS10-001 (Student in class 10)
                 SS5-001 (Student in class 5)
                 SS7-001 (Student in class 7)
        
        Args:
            db: Database session
            class_grade: The class/grade of the student (e.g., "10", "5", "7")
                         If not provided, defaults to generic "SS-XXX"
        """
        # Clean the class_grade - extract only numbers
        if class_grade:
            # Extract numbers from class_grade (e.g., "Class 10" -> "10")
            import re
            class_num = ''.join(re.findall(r'\d+', class_grade))
            if not class_num:
                class_num = "0"  # Default if no numbers found
        else:
            class_num = "0"  # Default if no class provided
        
        # Get all students to find the highest sequence number for this class
        all_students = db.query(Student).all()
        
        # Find max sequence number for this class
        max_seq = 0
        for student in all_students:
            # Check if student ID matches format SS{class}-XXX
            if f"SS{class_num}-" in student.student_id:
                try:
                    seq = int(student.student_id.split('-')[-1])
                    if seq > max_seq:
                        max_seq = seq
                except:
                    continue
        
        # Generate the new student ID
        next_seq = max_seq + 1
        new_id = f"SS{class_num}-{next_seq:03d}"
        
        return new_id
    
    @staticmethod
    def generate_family_id(db: Session) -> str:
        """
        Generate a unique family ID
        Format: FMYY00001
        Example: FM2600001 (First family in 2026)
                 FM2600002 (Second family in 2026)
                 FM2600003 (Third family in 2026)
        """
        year = datetime.now().year
        yy = str(year)[-2:]  # Get last 2 digits of year (e.g., "26" for 2026)
        
        # Get the last family ID to determine the sequence
        last_guardian = db.query(Guardian).order_by(Guardian.id.desc()).first()
        
        if last_guardian:
            # Extract the numeric part from the last family ID
            # Format: FMYY00001 -> Extract "00001"
            last_id_num = int(last_guardian.family_id[-5:])
            next_id_num = last_id_num + 1
        else:
            next_id_num = 1
        
        # Generate the new family ID
        new_id = f"FM{yy}{next_id_num:05d}"
        
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
        Format: FMYY00001-MMM
        Example: FM2600001-JAN (for January)
                 FM2600002-FEB (for February)
        
        Args:
            family_id: The family's registration ID (e.g., FM2600001)
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