"""
Fee Management Service
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import Student, FeeRecord, FeeStructure, FeeStatus, PaymentMethod, Guardian, FeeChallan
from app.utils.id_generator import IDGenerator

class FeeService:
    """Handle all fee-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.id_generator = IDGenerator()
    
    def create_fee_structure(self, data: dict) -> dict:
        """
        Create a new fee structure
        """
        try:
            fee_structure = FeeStructure(
                category=data['category'],
                description=data.get('description', ''),
                monthly_tuition_fee=float(data['monthly_fee']),
                admission_fee=float(data.get('admission_fee', 0)),
                annual_charges=float(data.get('annual_charges', data.get('exam_fee', 0))),
                transport_fee=float(data.get('transport_fee', 0)),
                discount_percentage=float(data.get('discount', 0)),
                default_payment_date=int(data.get('payment_date', 1))
            )
            
            self.db.add(fee_structure)
            self.db.commit()
            
            return {"success": True, "message": "Fee structure created successfully!"}
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_all_fee_structures(self):
        """Get all fee structures"""
        return self.db.query(FeeStructure).all()
    
    def generate_monthly_fees(self, month: int, year: int) -> dict:
        """
        Generate monthly fee records for all active students
        """
        try:
            # Get all active students
            students = self.db.query(Student).filter(
                Student.academic_status == "ACTIVE"
            ).all()
            
            count = 0
            for student in students:
                # Check if fee already generated for this month
                existing_fee = self.db.query(FeeRecord).filter(
                    FeeRecord.student_id == student.id,
                    FeeRecord.fee_type == "Monthly",
                    FeeRecord.due_date >= date(year, month, 1),
                    FeeRecord.due_date <= date(year, month, 28)
                ).first()
                
                if existing_fee:
                    continue
                
                # Calculate fee with discount
                monthly_fee = student.monthly_tuition_fee
                discount = student.discount_percentage / 100
                final_fee = monthly_fee - (monthly_fee * discount)
                
                # Create fee record
                fee_record = FeeRecord(
                    student_id=student.id,
                    fee_type="Monthly",
                    amount=final_fee,
                    paid_amount=0,
                    remaining_amount=final_fee,
                    due_date=date(year, month, student.default_payment_date),
                    status=FeeStatus.PENDING,
                    description=f"Monthly fee for {month}/{year}"
                )
                
                self.db.add(fee_record)
                count += 1
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Generated {count} monthly fee records for {month}/{year}"
            }
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def record_payment(self, fee_record_id: int, amount: float, payment_method: str) -> dict:
        """
        Record a payment for a fee record
        """
        try:
            fee_record = self.db.query(FeeRecord).filter(FeeRecord.id == fee_record_id).first()
            
            if not fee_record:
                return {"success": False, "message": "Fee record not found!"}
            
            # Update payment
            fee_record.paid_amount += amount
            fee_record.remaining_amount = fee_record.amount - fee_record.paid_amount
            fee_record.paid_date = date.today()
            fee_record.payment_method = PaymentMethod(payment_method.lower())
            fee_record.receipt_number = self.id_generator.generate_receipt_number()
            
            # Update status
            if fee_record.remaining_amount <= 0:
                fee_record.status = FeeStatus.PAID
            elif fee_record.paid_amount > 0:
                fee_record.status = FeeStatus.PARTIAL
            else:
                fee_record.status = FeeStatus.PENDING
            
            # Update student's total outstanding
            student = self.db.query(Student).filter(Student.id == fee_record.student_id).first()
            if student:
                # Recalculate total outstanding
                all_fees = self.db.query(FeeRecord).filter(
                    FeeRecord.student_id == student.id,
                    FeeRecord.status != FeeStatus.PAID
                ).all()
                
                total_outstanding = sum(fee.remaining_amount for fee in all_fees)
                student.total_outstanding_amount = total_outstanding
                student.last_payment_date = date.today()
                student.last_payment_amount = amount
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Payment recorded successfully!",
                "receipt_number": fee_record.receipt_number
            }
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_student_fees(self, student_id: int):
        """Get all fee records for a student"""
        return self.db.query(FeeRecord).filter(
            FeeRecord.student_id == student_id
        ).order_by(FeeRecord.due_date.desc()).all()
    
    def get_all_fee_records(self):
        """Get all fee records"""
        return self.db.query(FeeRecord).all()
    
    def get_outstanding_fees(self):
        """Get all outstanding fee records"""
        return self.db.query(FeeRecord).filter(
            FeeRecord.remaining_amount > 0
        ).all()
    
    def get_payment_history(self, student_id: int = None):
        """Get payment history"""
        query = self.db.query(FeeRecord).filter(FeeRecord.paid_amount > 0)
        
        if student_id:
            query = query.filter(FeeRecord.student_id == student_id)
        
        return query.order_by(FeeRecord.paid_date.desc()).all()
    
    def get_fee_summary(self):
        """Get fee summary statistics"""
        from sqlalchemy import func
        
        total_billed = self.db.query(FeeRecord).with_entities(
            func.sum(FeeRecord.amount)
        ).scalar() or 0
        
        total_collected = self.db.query(FeeRecord).with_entities(
            func.sum(FeeRecord.paid_amount)
        ).scalar() or 0
        
        total_outstanding = self.db.query(FeeRecord).with_entities(
            func.sum(FeeRecord.remaining_amount)
        ).scalar() or 0
        
        return {
            "total_billed": total_billed,
            "total_collected": total_collected,
            "total_outstanding": total_outstanding
        }
    
    def get_all_families_with_students(self):
        """Get all families with their students"""
        
        # Group students by family_id
        families = self.db.query(Guardian).all()
        
        families_data = []
        for family in families:
            # Get all students in this family
            students = self.db.query(Student).filter(
                Student.guardian_id == family.id
            ).all()
            
            if students:  # Only include families with students
                family_data = {
                    'family_id': family.family_id,
                    'guardian_name': family.guardian_name,
                    'guardian_cnic': family.cnic,
                    'guardian_contact': family.mobile_number,
                    'students': students,
                    'total_monthly_fee': sum(s.monthly_tuition_fee for s in students),
                    'total_fee_concession': sum(s.fee_concession for s in students),
                }
                families_data.append(family_data)
        
        return families_data
    
    def get_family_outstanding_amount(self, student_ids: list):
        """Get total outstanding amount for students in a family"""
        outstanding = self.db.query(FeeRecord).filter(
            FeeRecord.student_id.in_(student_ids),
            FeeRecord.remaining_amount > 0
        ).with_entities(
            func.sum(FeeRecord.remaining_amount)
        ).scalar() or 0
        
        return outstanding
    
    # ===== NEW METHOD: Get total outstanding amount using exact_payable and is_paid =====
    def get_family_outstanding_amount_for_month(self, family_id: str, current_month: str) -> float:
        """
        Get total outstanding/arrears amount for a FAMILY for a specific month.
        Uses exact_payable and is_paid fields to accurately track unpaid amounts.
        """
        # Define month order
        month_order = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        
        current_month_num = month_order.get(current_month, 1)
        
        # Get all challans for this family
        all_family_challans = self.db.query(FeeChallan).filter(
            FeeChallan.family_id == family_id
        ).all()
        
        total_outstanding = 0
        for challan in all_family_challans:
            challan_month = challan.challan_month
            challan_month_num = month_order.get(challan_month, 1)
            
            # Only count challans from months BEFORE the current month
            if challan_month_num < current_month_num:
                # If not paid, add the exact_payable for that month
                if not challan.is_paid:
                    total_outstanding += challan.exact_payable
        
        return total_outstanding
    
    # ===== KEEP THIS METHOD FOR BACKWARD COMPATIBILITY =====
    def get_student_outstanding_amount(self, student_id: int, current_month: str = None) -> float:
        """
        Get total outstanding/arrears amount for a single student.
        This is kept for backward compatibility but should NOT be used for family totals.
        """
        # Get the student
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return 0
        
        # Get the guardian for this student
        guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
        if not guardian:
            return 0
        
        # If current_month is provided, filter to only PREVIOUS months
        if current_month:
            # Use the family-level method to avoid double-counting
            return self.get_family_outstanding_amount_for_month(guardian.family_id, current_month)
        
        # If no current_month provided, sum all unpaid challans for this family
        outstanding = self.db.query(FeeChallan).filter(
            FeeChallan.family_id == guardian.family_id,
            FeeChallan.is_paid == False  # Only unpaid challans
        ).with_entities(
            func.sum(FeeChallan.exact_payable)
        ).scalar() or 0
        
        return outstanding
    
    def create_challan(self, challan_data: dict) -> dict:
        """Create a new fee challan - ONE PER FAMILY with all students combined"""
        try:
            # Get family details
            guardian = self.db.query(Guardian).filter(Guardian.family_id == challan_data['family_id']).first()
            
            if not guardian:
                return {"success": False, "message": "Family not found!"}
            
            # Check if challan already exists for this family for this month
            existing_challan = self.db.query(FeeChallan).filter(
                FeeChallan.family_id == challan_data['family_id'],
                FeeChallan.challan_month == challan_data['challan_month']
            ).first()
            
            if existing_challan:
                return {
                    "success": False, 
                    "message": f"Challan already exists for this family for {challan_data['challan_month']}!"
                }
            
            # Generate bill ID using FAMILY ID and SELECTED MONTH
            bill_id = self.id_generator.generate_bill_id(challan_data['family_id'], challan_data['challan_month'])
            
            # Get all students in this family
            students = self.db.query(Student).filter(
                Student.guardian_id == guardian.id
            ).all()
            
            if not students:
                return {"success": False, "message": "No students found for this family!"}
            
            # Calculate combined totals for ALL students
            total_monthly = sum(s.monthly_tuition_fee for s in students)
            total_concession = sum(s.fee_concession for s in students)
            
            # Calculate total arrears for the FAMILY (ONCE - not per student)
            total_arrears = self.get_family_outstanding_amount_for_month(
                challan_data['family_id'], challan_data['challan_month']
            )
            
            # Get the extra fees from challan_data
            admission_fee = float(challan_data.get('admission_fee', 0))
            registration_fee = float(challan_data.get('registration_fee', 0))
            exam_fee = float(challan_data.get('exam_fee', 0))
            transport_fee = float(challan_data.get('transport_fee', 0))
            other_fee = float(challan_data.get('other_fee', 0))
            
            # Build combined challan data
            total_amount = total_monthly + total_arrears + admission_fee + registration_fee + exam_fee + transport_fee + other_fee
            amount_due = total_amount - total_concession
            
            # Calculate exact_payable: This is the ACTUAL amount to pay for THIS month (after concession)
            exact_payable = total_monthly + admission_fee + registration_fee + exam_fee + transport_fee + other_fee - total_concession
            
            # Store students data as JSON for challan printing
            students_data = []
            for student in students:
                students_data.append({
                    'student_id': student.student_id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'class_grade': student.class_grade,
                    'section': student.section,
                    'monthly_fee': student.monthly_tuition_fee,
                    'concession': student.fee_concession,
                    'arrears': total_arrears  # Same for all students in family
                })
            
            # Create challan record - ONE PER FAMILY (INCLUDING ALL FEES)
            challan = FeeChallan(
                bill_id=bill_id,
                family_id=challan_data['family_id'],
                challan_month=challan_data['challan_month'],
                guardian_name=guardian.guardian_name,
                guardian_cnic=guardian.cnic,
                total_monthly_tuition_fee=total_monthly,
                total_admission_fee=admission_fee,
                total_registration_fee=registration_fee,  # ✅ ADDED
                total_exam_fee=exam_fee,
                total_transport_fee=transport_fee,        # ✅ ADDED
                total_other_fee=other_fee,
                total_arrears=total_arrears,
                total_fee_concession=total_concession,
                total_amount=total_amount,
                amount_due=amount_due,
                exact_payable=exact_payable,  # Store exact payable for this month
                is_paid=False,  # Default to unpaid
                paid_amount=0,
                remaining_amount=amount_due,
                urdu_footer=challan_data.get('urdu_footer', 'Please pay fees before the due date')
            )
            
            # Store students data as JSON in a separate field if needed (we'll use a method)
            self.db.add(challan)
            self.db.commit()
            
            return {
                "success": True,
                "message": "Challan created successfully!",
                "bill_id": bill_id,
                "challan_id": challan.id,
                "students_count": len(students)
            }
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_student_by_id(self, student_id: str):
        """Get student by student_id"""
        return self.db.query(Student).filter(Student.student_id == student_id).first()
    
    def get_guardian_by_family_id(self, family_id: str):
        """Get guardian by family_id"""
        return self.db.query(Guardian).filter(Guardian.family_id == family_id).first()
    
    def search_students_or_families(self, search_term: str):
        """Search for students or families by ID or name"""
        students = self.db.query(Student).filter(
            (Student.student_id.ilike(f"%{search_term}%")) |
            (Student.first_name.ilike(f"%{search_term}%")) |
            (Student.last_name.ilike(f"%{search_term}%"))
        ).all()
        
        return students
    
    def update_challan_status(self, challan_id: int, status: str, printed_date: date = None, payment_date: date = None, payment_method: str = None) -> dict:
        """Update challan status"""
        try:
            challan = self.db.query(FeeChallan).filter(FeeChallan.id == challan_id).first()
            if not challan:
                return {"success": False, "message": "Challan not found!"}
            
            challan.status = status
            if printed_date:
                challan.printed_date = printed_date
            if payment_date:
                challan.payment_date = payment_date
            if payment_method:
                challan.payment_method = payment_method
            
            # If status is PAID, set is_paid to True
            if status == "PAID":
                challan.is_paid = True
            
            self.db.commit()
            
            return {"success": True, "message": "Challan status updated successfully!"}
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_challan_by_bill_id(self, bill_id: str):
        """Get challan by bill ID"""
        return self.db.query(FeeChallan).filter(FeeChallan.bill_id == bill_id).first()
    
    def get_all_challans(self):
        """Get all challans"""
        return self.db.query(FeeChallan).order_by(FeeChallan.created_at.desc()).all()
    
    def get_challan_students(self, challan_id: int):
        """Get students associated with a challan"""
        challan = self.db.query(FeeChallan).filter(FeeChallan.id == challan_id).first()
        if not challan:
            return []
        
        guardian = self.db.query(Guardian).filter(Guardian.family_id == challan.family_id).first()
        if not guardian:
            return []
        
        return self.db.query(Student).filter(Student.guardian_id == guardian.id).all()