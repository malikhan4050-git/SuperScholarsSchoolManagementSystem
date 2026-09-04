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
    
    def __init__(self, db: Session):
        self.db = db
        self.id_generator = IDGenerator()
    
    def create_student(self, student_data: dict) -> dict:
        """
        Create a new student with guardian
        """
        try:
            # Get the class grade from student data
            class_grade = student_data.get('class_grade', '0')
            
            # Generate IDs - NOW PASSING CLASS_GRADE
            student_id = self.id_generator.generate_student_id(self.db, class_grade)
            family_id = self.id_generator.generate_family_id(self.db)
            
            # Create or get guardian
            guardian = self.create_or_get_guardian(student_data, family_id)
            
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
                monthly_tuition_fee=float(student_data.get('monthly_fee', 0)),
                fee_concession=float(student_data.get('fee_concession', 0)),  # Fee Concession
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=float(student_data.get('monthly_fee', 0))
            )
            
            self.db.add(student)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Student created successfully!",
                "student_id": student_id,
                "family_id": family_id
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
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(student, field):
                    setattr(student, field, value)
            
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