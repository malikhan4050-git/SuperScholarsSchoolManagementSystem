"""
Database Initializer for Super Scholars School Management System
"""

import sys
import os
from datetime import date, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.models import init_database, SessionLocal, User, UserRole, Student, Guardian, Gender, StudentStatus, FeeStatus
from app.utils.auth import SuperAdminSetup, PasswordManager
from app.utils.id_generator import IDGenerator
from app.services.student_service import StudentService  # Import for fee calculation

def setup_database():
    """Initialize database with default users and 1 sample student (1 family)"""
    
    print("=" * 60)
    print("SUPER SCHOLARS SCHOOL MANAGEMENT SYSTEM")
    print("Database Setup")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_database()
    
    # Create session
    db = SessionLocal()
    id_generator = IDGenerator()
    student_service = StudentService(db)  # Initialize for fee calculation
    
    try:
        # Setup Super Admin
        print("\n2. Setting up Super Admin...")
        result = SuperAdminSetup.create_super_admin(db)
        if result["success"]:
            print(f"   ✅ {result['message']}")
        else:
            print(f"   {result['message']}")
        
        # Create default Admin
        print("\n3. Creating default Admin...")
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not existing_admin:
            admin = User(
                username="admin",
                password_hash=PasswordManager.hash_password("Admin@123"),
                email="admin@superscholars.com",
                full_name="School Administrator",
                role=UserRole.ADMIN
            )
            db.add(admin)
            db.commit()
            print("   ✅ Admin created: username='admin', password='Admin@123'")
        else:
            print(f"   ✅ Admin already exists: username='{existing_admin.username}'")
        
        # Create default Principal
        print("\n4. Creating default Principal...")
        existing_principal = db.query(User).filter(User.role == UserRole.PRINCIPAL).first()
        if not existing_principal:
            principal = User(
                username="principal",
                password_hash=PasswordManager.hash_password("Principal@123"),
                email="principal@superscholars.com",
                full_name="School Principal",
                role=UserRole.PRINCIPAL
            )
            db.add(principal)
            db.commit()
            print("   ✅ Principal created: username='principal', password='Principal@123'")
        else:
            print(f"   ✅ Principal already exists: username='{existing_principal.username}'")
        
        # Create Single Family (1 student) - EXAMPLE FAMILY
        print("\n5. Creating Sample Family (1 student)...")
        existing_guardian = db.query(Guardian).filter(Guardian.cnic == "12345-1234567-1").first()
        if not existing_guardian:
            family_id = id_generator.generate_family_id(db)
            
            guardian = Guardian(
                family_id=family_id,
                guardian_name="Muhammad Ahmed",
                relationship="Father",
                cnic="12345-1234567-1",
                mobile_number="0300-1234567",
                email="ahmed@example.com",
                occupation="Businessman",
                monthly_income=50000.0,
                address="House 123, Street 45, F-8/4, Islamabad",
                permanent_address="House 123, Street 45, F-8/4, Islamabad",
                emergency_contact_name="Fatima Ahmed",
                emergency_contact_number="0301-7654321"
            )
            db.add(guardian)
            db.flush()
            
            # Create Single Student - Class 5 (Fee will be AUTO-CALCULATED)
            student_id = id_generator.generate_student_id(db, "Class 5")
            
            # Auto-calculate fee using StudentService (no hardcoded fee)
            class_grade = "Class 5"
            monthly_fee = student_service.get_fee_for_class(class_grade)  # This will return Rs. 2,000
            fee_concession = 500.0
            
            student = Student(
                student_id=student_id,
                first_name="Ali",
                last_name="Ahmed",
                date_of_birth=date(2013, 5, 15),
                gender=Gender.MALE,
                cnic_bform="12345-1234567-1",
                guardian_id=guardian.id,
                admission_date=date(2026, 8, 1),
                class_grade=class_grade,
                section="A",
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=monthly_fee,  # Auto-calculated
                fee_concession=fee_concession,
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=monthly_fee - fee_concession  # Net fee
            )
            db.add(student)
            db.commit()
            
            print(f"   ✅ Sample Family created (Family ID: {family_id})")
            print(f"   ✅ Ali Ahmed (ID: {student_id}) - Class 5 - Fee: Rs. {monthly_fee:,.0f}/month - Concession: Rs. {fee_concession:,.0f} (Net: Rs. {monthly_fee - fee_concession:,.0f})")
        else:
            print(f"   ✅ Sample Family already exists")
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed successfully!")
        print("=" * 60)
        
        print("\n📋 Default Credentials:")
        print("   Super Admin: superadmin / Admin@123")
        print("   Admin:       admin / Admin@123")
        print("   Principal:   principal / Principal@123")
        
        print("\n📋 Sample Student:")
        print("   Family ID: FM26-1")
        print("   Ali Ahmed - Class 5 - Fee: Rs. 2,000/month - Concession: Rs. 500 (Net: Rs. 1,500)")
        print("   (Fee is auto-calculated based on class)")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()