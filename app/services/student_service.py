"""
Student Management Service
"""

from sqlalchemy.orm import Session
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import Student, Guardian, Gender, StudentStatus, FeeStatus
from app.utils.id_generator import IDGenerator

class StudentService:
    """Handle all student-related operations"""
    
    # Class-Based Fee Structure
    CLASS_FEE_STRUCTURE = {
        "1": 1500,
        "2": 1500,
        "3": 1500,
        "4": 1800,
        "5": 2000,
        "6": 2200,
        "7": 2400,
        "8": 2600,
        "9": 2500,
        "10": 3000,
        "11": 3500,
        "12": 4000,
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.id_generator = IDGenerator()
    
    def get_fee_for_class(self, class_grade: str) -> float:
        """
        Get the monthly fee for a specific class
        """
        # Clean the class_grade - extract only numbers
        import re
        class_num = ''.join(re.findall(r'\d+', class_grade))
        
        if class_num in self.CLASS_FEE_STRUCTURE:
            return self.CLASS_FEE_STRUCTURE[class_num]
        else:
            # Default fee if class not in structure
            return 2000.0
    
    def create_student(self, student_data: dict) -> dict:
        """
        Create a new student with guardian
        """
        try:
            # Get the class grade from student data
            class_grade = student_data.get('class_grade', '0')
            
            # Generate IDs
            student_id = self.id_generator.generate_student_id(self.db, class_grade)
            family_id = self.id_generator.generate_family_id(self.db)
            
            # Create or get guardian
            guardian = self.create_or_get_guardian(student_data, family_id)
            
            # Get the monthly fee based on class (if not provided in data)
            monthly_fee = float(student_data.get('monthly_fee', 0))
            if monthly_fee == 0:
                monthly_fee = self.get_fee_for_class(class_grade)
            
            # Create student
            student = Student(
                student_id=student_id,
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                date_of_birth=datetime.strptime(student_data['dob'], '%Y-%m-%d').date(),
                gender=Gender(student_data['gender'].lower()),
                cnic_bform=student_data.get('cnic', ''),
                guardian_id=guardian.id,
                admission_date=datetime.strptime(student_data['admission_date'], '%Y-%m-%d').date(),
                class_grade=class_grade,
                section=student_data.get('section', ''),
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=monthly_fee,
                fee_concession=float(student_data.get('fee_concession', 0)),
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=monthly_fee
            )
            
            self.db.add(student)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Student created successfully!",
                "student_id": student_id,
                "family_id": family_id,
                "monthly_fee": monthly_fee
            }
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def create_or_get_guardian(self, data: dict, family_id: str) -> Guardian:
        """
        Create a new guardian or get existing one
        """
        # Check if guardian with this CNIC exists
        guardian_cnic = data.get('guardian_cnic', '')
        guardian = self.db.query(Guardian).filter(Guardian.cnic == guardian_cnic).first()
        
        if guardian:
            return guardian
        
        # Create new guardian
        guardian = Guardian(
            family_id=family_id,
            guardian_name=data.get('guardian_name', ''),
            relationship='Parent',
            cnic=guardian_cnic,
            mobile_number=data.get('mobile', ''),
            email=data.get('email', ''),
            occupation=data.get('guardian_occupation', ''),
            monthly_income=float(data.get('guardian_income', 0)),
            address=data.get('current_address', ''),
            permanent_address=data.get('permanent_address', ''),
            emergency_contact_name=data.get('emergency_name', ''),
            emergency_contact_number=data.get('emergency_phone', '')
        )
        
        self.db.add(guardian)
        self.db.flush()  # Get guardian ID without committing
        
        return guardian
    
    def get_all_students(self):
        """Get all students"""
        return self.db.query(Student).all()
    
    def get_student_by_id(self, student_id: int):
        """Get student by database ID"""
        return self.db.query(Student).filter(Student.id == student_id).first()
    
    def get_student_by_student_id(self, student_id: str):
        """Get student by custom ID"""
        return self.db.query(Student).filter(Student.student_id == student_id).first()
    
    def update_student(self, student_id: int, update_data: dict) -> dict:
        """
        Update student information
        """
        try:
            student = self.get_student_by_id(student_id)
            
            if not student:
                return {"success": False, "message": "Student not found!"}
            
            # Get the guardian for this student
            guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
            
            # Update student fields
            if 'first_name' in update_data:
                student.first_name = update_data['first_name']
            if 'last_name' in update_data:
                student.last_name = update_data['last_name']
            if 'dob' in update_data:
                student.date_of_birth = datetime.strptime(update_data['dob'], '%Y-%m-%d').date()
            if 'gender' in update_data:
                student.gender = Gender(update_data['gender'].lower())
            if 'cnic' in update_data:
                student.cnic_bform = update_data['cnic']
            if 'class_grade' in update_data:
                student.class_grade = update_data['class_grade']
                # Auto-update monthly fee based on new class
                student.monthly_tuition_fee = self.get_fee_for_class(update_data['class_grade'])
            if 'section' in update_data:
                student.section = update_data['section']
            if 'monthly_fee' in update_data:
                student.monthly_tuition_fee = float(update_data['monthly_fee'])
            if 'fee_concession' in update_data:
                student.fee_concession = float(update_data['fee_concession'])
            
            # Update guardian fields
            if guardian:
                if 'guardian_name' in update_data:
                    guardian.guardian_name = update_data['guardian_name']
                if 'guardian_cnic' in update_data:
                    guardian.cnic = update_data['guardian_cnic']
                if 'mobile' in update_data:
                    guardian.mobile_number = update_data['mobile']
                if 'email' in update_data:
                    guardian.email = update_data['email']
                if 'current_address' in update_data:
                    guardian.address = update_data['current_address']
                if 'permanent_address' in update_data:
                    guardian.permanent_address = update_data['permanent_address']
                if 'guardian_occupation' in update_data:
                    guardian.occupation = update_data['guardian_occupation']
                if 'guardian_income' in update_data:
                    guardian.monthly_income = float(update_data['guardian_income'])
                if 'emergency_name' in update_data:
                    guardian.emergency_contact_name = update_data['emergency_name']
                if 'emergency_phone' in update_data:
                    guardian.emergency_contact_number = update_data['emergency_phone']
            
            self.db.commit()
            
            return {"success": True, "message": "Student updated successfully!"}
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def delete_student(self, student_id: int) -> dict:
        """
        Delete a student
        """
        try:
            student = self.get_student_by_id(student_id)
            
            if not student:
                return {"success": False, "message": "Student not found!"}
            
            self.db.delete(student)
            self.db.commit()
            
            return {"success": True, "message": "Student deleted successfully!"}
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def search_students(self, search_term: str):
        """
        Search students by name or ID
        """
        search_term = f"%{search_term}%"
        return self.db.query(Student).filter(
            (Student.first_name.ilike(search_term)) |
            (Student.last_name.ilike(search_term)) |
            (Student.student_id.ilike(search_term))
        ).all()
    
    def get_students_by_class(self, class_grade: str):
        """
        Get all students in a specific class
        """
        return self.db.query(Student).filter(Student.class_grade == class_grade).all()
    
    def get_next_class(self, class_grade: str) -> str:
        """
        Get the next class for promotion
        """
        # Clean the class_grade - extract only numbers
        import re
        class_num = ''.join(re.findall(r'\d+', class_grade))
        
        if class_num:
            try:
                next_class_num = int(class_num) + 1
                # Return as "Class X" format
                return f"Class {next_class_num}"
            except:
                return class_grade
        else:
            return class_grade
    
    def promote_students(self, student_ids: list, current_class: str) -> dict:
        """
        Promote selected students to the next class
        """
        try:
            if not student_ids:
                return {"success": False, "message": "No students selected for promotion!"}
            
            promoted_count = 0
            next_class = self.get_next_class(current_class)
            next_class_fee = self.get_fee_for_class(next_class)
            
            for student_id in student_ids:
                student = self.get_student_by_id(student_id)
                if student:
                    # Update class grade
                    student.class_grade = next_class
                    # Update monthly fee based on new class
                    student.monthly_tuition_fee = next_class_fee
                    promoted_count += 1
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Successfully promoted {promoted_count} students to {next_class}!",
                "promoted_count": promoted_count,
                "next_class": next_class
            }
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def promote_all_students_in_class(self, class_grade: str) -> dict:
        """
        Promote all students in a class to the next class
        """
        try:
            # Get all students in this class
            students = self.get_students_by_class(class_grade)
            
            if not students:
                return {"success": False, "message": f"No students found in {class_grade}!"}
            
            next_class = self.get_next_class(class_grade)
            next_class_fee = self.get_fee_for_class(next_class)
            
            promoted_count = 0
            for student in students:
                student.class_grade = next_class
                student.monthly_tuition_fee = next_class_fee
                promoted_count += 1
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Successfully promoted all {promoted_count} students from {class_grade} to {next_class}!",
                "promoted_count": promoted_count,
                "next_class": next_class
            }
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}