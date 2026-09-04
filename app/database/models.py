"""
Database models for Super Scholars School Management System
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, DateTime, Boolean, Text, Enum, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, date
import enum

# Create base class for all models
Base = declarative_base()

# Database file path
DATABASE_URL = "sqlite:///super_scholars.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Define Enums
class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PRINCIPAL = "principal"

class StudentStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    SUSPENDED = "suspended"

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class FeeStatus(enum.Enum):
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    PARTIAL = "partial"

class PaymentMethod(enum.Enum):
    CASH = "cash"
    BANK = "bank"
    CARD = "card"
    ONLINE = "online"

class User(Base):
    """User Model for Authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    email = Column(String(100), unique=True)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ADMIN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class Guardian(Base):
    """Guardian/Family Model"""
    __tablename__ = "guardians"
    
    id = Column(Integer, primary_key=True)
    family_id = Column(String(20), unique=True, nullable=False)  # FMYY00001 format
    guardian_name = Column(String(100), nullable=False)
    relationship = Column(String(50), nullable=False)
    cnic = Column(String(15), unique=True)
    mobile_number = Column(String(15), nullable=False)
    email = Column(String(100))
    occupation = Column(String(100))
    monthly_income = Column(Float)
    address = Column(String(200))
    permanent_address = Column(String(200))
    emergency_contact_name = Column(String(100))
    emergency_contact_number = Column(String(15))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Guardian('{self.guardian_name}', '{self.family_id}')"

class Student(Base):
    """Student Model"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(20), unique=True, nullable=False)  # SS5-001 format
    
    # Personal Information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    cnic_bform = Column(String(15), unique=True)
    
    # Guardian/Family Information
    guardian_id = Column(Integer, ForeignKey("guardians.id"))
    
    # Academic Information
    admission_date = Column(Date, nullable=False, default=date.today)
    class_grade = Column(String(20), nullable=False)
    section = Column(String(10))
    academic_status = Column(Enum(StudentStatus), default=StudentStatus.ACTIVE)
    
    # Fee-Specific Fields
    monthly_tuition_fee = Column(Float, nullable=False, default=0.0)
    fee_concession = Column(Float, default=0.0)  # Fee Concession Amount
    
    # Fee Status
    fee_status = Column(Enum(FeeStatus), default=FeeStatus.PENDING)
    total_outstanding_amount = Column(Float, default=0.0)
    last_payment_date = Column(Date)
    last_payment_amount = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"Student('{self.student_id}', '{self.full_name}')"

class Teacher(Base):
    """Teacher Model"""
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    hire_date = Column(Date, default=date.today)
    department = Column(String(100))
    qualification = Column(String(200))
    status = Column(String(20), default="active")  # active, inactive, on_leave
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"Teacher('{self.first_name} {self.last_name}')"

class FeeStructure(Base):
    """Fee Structure Model"""
    __tablename__ = "fee_structures"
    
    id = Column(Integer, primary_key=True)
    category = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    monthly_tuition_fee = Column(Float, nullable=False)
    admission_fee = Column(Float, default=0.0)
    annual_charges = Column(Float, default=0.0)
    transport_fee = Column(Float, default=0.0)
    discount_percentage = Column(Float, default=0.0)
    default_payment_date = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"FeeStructure('{self.category}', {self.monthly_tuition_fee})"

class FeeRecord(Base):
    """Fee Record Model"""
    __tablename__ = "fee_records"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    fee_type = Column(String(50), nullable=False)  # Monthly, Admission, Exam, Transport
    amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date)
    status = Column(Enum(FeeStatus), default=FeeStatus.PENDING)
    payment_method = Column(Enum(PaymentMethod))
    receipt_number = Column(String(50))
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"FeeRecord(Student: {self.student_id}, Amount: {self.amount})"

class AuditLog(Base):
    """Audit Log Model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(200), nullable=False)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))
    
    def __repr__(self):
        return f"AuditLog(User: {self.user_id}, Action: {self.action})"

class FeeChallan(Base):
    """Fee Challan Model for tracking generated challans - ONE PER FAMILY"""
    __tablename__ = "fee_challans"
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(String(50), unique=True, nullable=False)  # FM2600001-JAN
    family_id = Column(String(20), nullable=False)  # FMYY00001 format - ONE challan per family
    challan_month = Column(String(20), nullable=False)  # e.g., "January"
    challan_year = Column(String(10), default=str(datetime.now().year))  # Field for year
    
    # Due Date for the challan
    due_date = Column(Date, default=date.today)  # NEW FIELD - Due date for the challan
    
    # Guardian/Student Information (Stored for quick access)
    guardian_name = Column(String(100), default="")
    guardian_cnic = Column(String(15), default="")
    
    # Total Fee Breakdown (Combined for ALL students in family)
    total_monthly_tuition_fee = Column(Float, default=0.0)
    total_id_card_fee = Column(Float, default=0.0)
    total_books_fee = Column(Float, default=0.0)
    total_exam_fee = Column(Float, default=0.0)
    total_security_fee = Column(Float, default=0.0)
    total_admission_fee = Column(Float, default=0.0)
    total_registration_fee = Column(Float, default=0.0)  # Field for registration fee
    total_transport_fee = Column(Float, default=0.0)      # Field for transport fee
    total_other_fee = Column(Float, default=0.0)
    total_arrears = Column(Float, default=0.0)
    total_scholarship = Column(Float, default=0.0)
    total_fee_concession = Column(Float, default=0.0)
    
    # Total Amount
    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)  # After scholarship and concession
    
    # PAYMENT TRACKING - NEW FIELDS
    exact_payable = Column(Float, default=0.0)  # Actual amount to pay for THIS month (after concession)
    is_paid = Column(Boolean, default=False)    # Whether this month's challan has been paid
    
    # Payment Tracking Fields
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)
    
    # Receipt Number
    receipt_number = Column(String(50))
    
    # Status and Metadata
    status = Column(String(20), default="Generated")  # Generated, Printed, Paid
    printed_date = Column(Date)
    payment_date = Column(Date)
    payment_method = Column(String(50))
    
    # Urdu Footer Text
    urdu_footer = Column(Text, default="براہ کرم مقررہ تاریخ سے پہلے فیس جمع کرائیں")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"FeeChallan(Bill ID: {self.bill_id}, Family: {self.family_id}, Month: {self.challan_month} {self.challan_year}, Due: {self.due_date}, Amount: {self.total_amount})"

# Create all tables
def init_database():
    """Initialize the database and create all tables"""
    Base.metadata.create_all(bind=engine)

    guardian_columns = {
        column["name"] for column in inspect(engine).get_columns("guardians")
    }
    if "permanent_address" not in guardian_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE guardians ADD COLUMN permanent_address VARCHAR(200)")
            )
    
    # Check if fee_concession column exists in students table
    student_columns = {
        column["name"] for column in inspect(engine).get_columns("students")
    }
    if "fee_concession" not in student_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE students ADD COLUMN fee_concession FLOAT DEFAULT 0.0")
            )
    
    # Check if family_id column exists in fee_challans table
    challan_columns = {
        column["name"] for column in inspect(engine).get_columns("fee_challans")
    }
    if "family_id" not in challan_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE fee_challans ADD COLUMN family_id VARCHAR(20)")
            )
    
    # Check if exact_payable column exists in fee_challans table
    if "exact_payable" not in challan_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE fee_challans ADD COLUMN exact_payable FLOAT DEFAULT 0.0")
            )
    
    # Check if is_paid column exists in fee_challans table
    if "is_paid" not in challan_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE fee_challans ADD COLUMN is_paid BOOLEAN DEFAULT 0")
            )
    
    # Check if total_registration_fee column exists
    if "total_registration_fee" not in challan_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE fee_challans ADD COLUMN total_registration_fee FLOAT DEFAULT 0.0")
            )
    
    # Check if total_transport_fee column exists
    if "total_transport_fee" not in challan_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE fee_challans ADD COLUMN total_transport_fee FLOAT DEFAULT 0.0")
            )
    
    # Check if challan_year column exists
    if "challan_year" not in challan_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE fee_challans ADD COLUMN challan_year VARCHAR(10) DEFAULT '2026'")
            )
    
    # Check if due_date column exists
    if "due_date" not in challan_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE fee_challans ADD COLUMN due_date DATE")
            )
    
    # Check if student_id column exists in fee_challans table (for backward compatibility)
    if "student_id" in challan_columns:
        # We can keep it for now, but it's no longer the primary identifier
        pass
    
    print("✅ Database initialized successfully!")

# Test the database
if __name__ == "__main__":
    init_database()
    print("Database file created: super_scholars.db")