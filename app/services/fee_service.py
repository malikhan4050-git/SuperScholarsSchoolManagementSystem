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
        """Create a new fee structure"""
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
        """Generate monthly fee records for all active students"""
        try:
            students = self.db.query(Student).filter(
                Student.academic_status == "ACTIVE"
            ).all()
            
            count = 0
            for student in students:
                existing_fee = self.db.query(FeeRecord).filter(
                    FeeRecord.student_id == student.id,
                    FeeRecord.fee_type == "Monthly",
                    FeeRecord.due_date >= date(year, month, 1),
                    FeeRecord.due_date <= date(year, month, 28)
                ).first()
                
                if existing_fee:
                    continue
                
                monthly_fee = student.monthly_tuition_fee
                discount = student.discount_percentage / 100
                final_fee = monthly_fee - (monthly_fee * discount)
                
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
        """Record a payment for a fee record"""
        try:
            fee_record = self.db.query(FeeRecord).filter(FeeRecord.id == fee_record_id).first()
            
            if not fee_record:
                return {"success": False, "message": "Fee record not found!"}
            
            fee_record.paid_amount += amount
            fee_record.remaining_amount = fee_record.amount - fee_record.paid_amount
            fee_record.paid_date = date.today()
            fee_record.payment_method = PaymentMethod(payment_method.lower())
            fee_record.receipt_number = self.id_generator.generate_receipt_number()
            
            if fee_record.remaining_amount <= 0:
                fee_record.status = FeeStatus.PAID
            elif fee_record.paid_amount > 0:
                fee_record.status = FeeStatus.PARTIAL
            else:
                fee_record.status = FeeStatus.PENDING
            
            student = self.db.query(Student).filter(Student.id == fee_record.student_id).first()
            if student:
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
        families = self.db.query(Guardian).all()
        
        families_data = []
        for family in families:
            students = self.db.query(Student).filter(
                Student.guardian_id == family.id
            ).all()
            
            if students:
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
    
    def get_family_outstanding_amount_for_month(self, family_id: str, current_month: str, current_year: str = None) -> float:
        """Get total outstanding/arrears amount for a FAMILY for a specific month"""
        month_order = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        
        current_month_num = month_order.get(current_month, 1)
        current_year_num = int(current_year) if current_year else datetime.now().year
        
        all_family_challans = self.db.query(FeeChallan).filter(
            FeeChallan.family_id == family_id
        ).all()
        
        total_outstanding = 0
        for challan in all_family_challans:
            challan_month = challan.challan_month
            challan_month_num = month_order.get(challan_month, 1)
            challan_year_num = int(challan.challan_year) if challan.challan_year else datetime.now().year
            
            if challan_year_num < current_year_num:
                # Previous years - all unpaid challans count (remaining_amount)
                if not challan.is_paid:
                    total_outstanding += challan.remaining_amount  # FIXED: was exact_payable
            elif challan_year_num == current_year_num:
                # Same year - only count months BEFORE current month
                if challan_month_num < current_month_num:
                    if not challan.is_paid:
                        total_outstanding += challan.remaining_amount  # FIXED: was exact_payable
        
        return total_outstanding
    
    def get_student_outstanding_amount(self, student_id: int, current_month: str = None, current_year: str = None) -> float:
        """Get total outstanding/arrears amount for a single student"""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return 0
        
        guardian = self.db.query(Guardian).filter(Guardian.id == student.guardian_id).first()
        if not guardian:
            return 0
        
        if current_month:
            return self.get_family_outstanding_amount_for_month(guardian.family_id, current_month, current_year)
        
        outstanding = self.db.query(FeeChallan).filter(
            FeeChallan.family_id == guardian.family_id,
            FeeChallan.is_paid == False
        ).with_entities(
            func.sum(FeeChallan.remaining_amount)  # FIXED: was exact_payable
        ).scalar() or 0
        
        return outstanding
    
    def check_challan_exists(self, family_id: str, challan_month: str, challan_year: str = None) -> bool:
        """Check if a challan already exists for a family for a specific month/year"""
        if not challan_year:
            challan_year = str(datetime.now().year)
        
        existing_challan = self.db.query(FeeChallan).filter(
            FeeChallan.family_id == family_id,
            FeeChallan.challan_month == challan_month,
            FeeChallan.challan_year == challan_year
        ).first()
        
        return existing_challan is not None
    
    def create_challan(self, challan_data: dict) -> dict:
        """Create a new fee challan - ONE PER FAMILY with all students combined"""
        try:
            guardian = self.db.query(Guardian).filter(Guardian.family_id == challan_data['family_id']).first()
            
            if not guardian:
                return {"success": False, "message": "Family not found!"}
            
            existing_challan = self.db.query(FeeChallan).filter(
                FeeChallan.family_id == challan_data['family_id'],
                FeeChallan.challan_month == challan_data['challan_month'],
                FeeChallan.challan_year == challan_data.get('challan_year', str(datetime.now().year))
            ).first()
            
            if existing_challan:
                return {
                    "success": False,
                    "message": f"Challan already exists for this family for {challan_data['challan_month']} {challan_data.get('challan_year', '')}!",
                    "challan_exists": True
                }
            
            bill_id = self.id_generator.generate_bill_id(challan_data['family_id'], challan_data['challan_month'])
            
            students = self.db.query(Student).filter(
                Student.guardian_id == guardian.id
            ).all()
            
            if not students:
                return {"success": False, "message": "No students found for this family!"}
            
            total_monthly = sum(s.monthly_tuition_fee for s in students)
            total_concession = sum(s.fee_concession for s in students)
            
            challan_year = challan_data.get('challan_year', str(datetime.now().year))
            
            due_date_str = challan_data.get('due_date', date.today().strftime("%Y-%m-%d"))
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                due_date = date.today()
            
            # FIXED: Use the total_arrears from challan_data if provided, otherwise calculate
            if 'total_arrears' in challan_data and challan_data.get('total_arrears') is not None:
                total_arrears = float(challan_data.get('total_arrears', 0))
            else:
                total_arrears = self.get_family_outstanding_amount_for_month(
                    challan_data['family_id'], challan_data['challan_month'], challan_year
                )
            
            admission_fee = float(challan_data.get('admission_fee', 0))
            registration_fee = float(challan_data.get('registration_fee', 0))
            exam_fee = float(challan_data.get('exam_fee', 0))
            transport_fee = float(challan_data.get('transport_fee', 0))
            other_fee = float(challan_data.get('other_fee', 0))
            
            total_amount = total_monthly + total_arrears + admission_fee + registration_fee + exam_fee + transport_fee + other_fee
            amount_due = total_amount - total_concession
            
            exact_payable = total_monthly + admission_fee + registration_fee + exam_fee + transport_fee + other_fee - total_concession
            
            challan = FeeChallan(
                bill_id=bill_id,
                family_id=challan_data['family_id'],
                challan_month=challan_data['challan_month'],
                challan_year=challan_year,
                due_date=due_date,
                guardian_name=guardian.guardian_name,
                guardian_cnic=guardian.cnic,
                total_monthly_tuition_fee=total_monthly,
                total_admission_fee=admission_fee,
                total_registration_fee=registration_fee,
                total_exam_fee=exam_fee,
                total_transport_fee=transport_fee,
                total_other_fee=other_fee,
                total_arrears=total_arrears,  # FIXED: Use provided value
                total_fee_concession=total_concession,
                total_amount=total_amount,
                amount_due=amount_due,
                exact_payable=exact_payable,
                is_paid=False,
                paid_amount=0,
                remaining_amount=amount_due,
                urdu_footer=challan_data.get('urdu_footer', 'Please pay fees before the due date')
            )
            
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
    
    def replace_challan(self, family_id: str, challan_month: str, challan_year: str = None) -> bool:
        """Delete existing challan for a family/month/year"""
        try:
            if not challan_year:
                challan_year = str(datetime.now().year)
            
            existing_challan = self.db.query(FeeChallan).filter(
                FeeChallan.family_id == family_id,
                FeeChallan.challan_month == challan_month,
                FeeChallan.challan_year == challan_year
            ).first()
            
            if existing_challan:
                self.db.delete(existing_challan)
                self.db.commit()
                print(f"Deleted existing challan for {family_id} - {challan_month} {challan_year}")
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            print(f"Error replacing challan: {str(e)}")
            return False
    
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