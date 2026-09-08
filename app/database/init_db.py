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

def setup_database():
    """Initialize database with default users and 8 sample students (4 families)"""
    
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
        
        # Create Family 1 (2 students) - AHMED FAMILY
        print("\n5. Creating Family 1 (Ahmed Family - 2 students)...")
        existing_guardian1 = db.query(Guardian).filter(Guardian.cnic == "12345-1234567-1").first()
        if not existing_guardian1:
            family1_id = id_generator.generate_family_id(db)
            
            guardian1 = Guardian(
                family_id=family1_id,
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
            db.add(guardian1)
            db.flush()
            
            # Student 1 - Class 5 (Fee: Rs. 1,500)
            student1_id = id_generator.generate_student_id(db, "Class 5")
            student1 = Student(
                student_id=student1_id,
                first_name="Ali",
                last_name="Ahmed",
                date_of_birth=date(2013, 5, 15),
                gender=Gender.MALE,
                cnic_bform="12345-1234567-1",
                guardian_id=guardian1.id,
                admission_date=date(2026, 8, 1),
                class_grade="Class 5",
                section="A",
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=1500.0,  # Changed to 1500
                fee_concession=500.0,
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=1500.0
            )
            db.add(student1)
            db.commit()
            
            # Student 2 - Class 3 (Fee: Rs. 1,500)
            student2_id = id_generator.generate_student_id(db, "Class 3")
            student2 = Student(
                student_id=student2_id,
                first_name="Sara",
                last_name="Ahmed",
                date_of_birth=date(2015, 9, 20),
                gender=Gender.FEMALE,
                cnic_bform="12345-7654321-1",
                guardian_id=guardian1.id,
                admission_date=date(2026, 8, 1),
                class_grade="Class 3",
                section="B",
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=1500.0,  # Changed to 1500
                fee_concession=500.0,
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=1500.0
            )
            db.add(student2)
            db.commit()
            
            print(f"   ✅ Ahmed Family created (Family ID: {family1_id})")
            print(f"   ✅ Ali Ahmed (ID: {student1_id}) - Class 5 - Rs. 1,500/month - Concession: Rs. 500")
            print(f"   ✅ Sara Ahmed (ID: {student2_id}) - Class 3 - Rs. 1,500/month - Concession: Rs. 500")
        else:
            print(f"   ✅ Ahmed Family already exists")
        
        # Create Family 2 (2 students) - KHAN FAMILY
        print("\n6. Creating Family 2 (Khan Family - 2 students)...")
        existing_guardian2 = db.query(Guardian).filter(Guardian.cnic == "12345-9876543-1").first()
        if not existing_guardian2:
            family2_id = id_generator.generate_family_id(db)
            
            guardian2 = Guardian(
                family_id=family2_id,
                guardian_name="Imran Khan",
                relationship="Father",
                cnic="12345-9876543-1",
                mobile_number="0300-9876543",
                email="khan@example.com",
                occupation="Engineer",
                monthly_income=80000.0,
                address="House 456, Street 12, F-10/3, Islamabad",
                permanent_address="House 456, Street 12, F-10/3, Islamabad",
                emergency_contact_name="Ayesha Khan",
                emergency_contact_number="0301-1234567"
            )
            db.add(guardian2)
            db.flush()
            
            # Student 3 - Class 7 (Fee: Rs. 1,500)
            student3_id = id_generator.generate_student_id(db, "Class 7")
            student3 = Student(
                student_id=student3_id,
                first_name="Hamza",
                last_name="Khan",
                date_of_birth=date(2012, 2, 10),
                gender=Gender.MALE,
                cnic_bform="12345-9876543-1",
                guardian_id=guardian2.id,
                admission_date=date(2026, 8, 1),
                class_grade="Class 7",
                section="A",
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=1500.0,  # Changed to 1500
                fee_concession=500.0,
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=1500.0
            )
            db.add(student3)
            db.commit()
            
            # Student 4 - Class 6 (Fee: Rs. 1,500)
            student4_id = id_generator.generate_student_id(db, "Class 6")
            student4 = Student(
                student_id=student4_id,
                first_name="Zainab",
                last_name="Khan",
                date_of_birth=date(2014, 11, 25),
                gender=Gender.FEMALE,
                cnic_bform="12345-6543210-1",
                guardian_id=guardian2.id,
                admission_date=date(2026, 8, 1),
                class_grade="Class 6",
                section="B",
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=1500.0,  # Changed to 1500
                fee_concession=500.0,
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=1500.0
            )
            db.add(student4)
            db.commit()
            
            print(f"   ✅ Khan Family created (Family ID: {family2_id})")
            print(f"   ✅ Hamza Khan (ID: {student3_id}) - Class 7 - Rs. 1,500/month - Concession: Rs. 500")
            print(f"   ✅ Zainab Khan (ID: {student4_id}) - Class 6 - Rs. 1,500/month - Concession: Rs. 500")
        else:
            print(f"   ✅ Khan Family already exists")
        
        # Create Family 3 (2 students) - MALIK FAMILY
        print("\n7. Creating Family 3 (Malik Family - 2 students)...")
        existing_guardian3 = db.query(Guardian).filter(Guardian.cnic == "12345-1111111-1").first()
        if not existing_guardian3:
            family3_id = id_generator.generate_family_id(db)
            
            guardian3 = Guardian(
                family_id=family3_id,
                guardian_name="Rashid Malik",
                relationship="Father",
                cnic="12345-1111111-1",
                mobile_number="0300-1111111",
                email="malik@example.com",
                occupation="Teacher",
                monthly_income=60000.0,
                address="House 789, Street 22, F-11/2, Islamabad",
                permanent_address="House 789, Street 22, F-11/2, Islamabad",
                emergency_contact_name="Amina Malik",
                emergency_contact_number="0301-2222222"
            )
            db.add(guardian3)
            db.flush()
            
            # Student 5 - Class 4 (Fee: Rs. 1,500)
            student5_id = id_generator.generate_student_id(db, "Class 4")
            student5 = Student(
                student_id=student5_id,
                first_name="Usman",
                last_name="Malik",
                date_of_birth=date(2014, 3, 15),
                gender=Gender.MALE,
                cnic_bform="12345-1111111-1",
                guardian_id=guardian3.id,
                admission_date=date(2026, 8, 1),
                class_grade="Class 4",
                section="A",
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=1500.0,  # Set to 1500
                fee_concession=500.0,
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=1500.0
            )
            db.add(student5)
            db.commit()
            
            # Student 6 - Class 2 (Fee: Rs. 1,500)
            student6_id = id_generator.generate_student_id(db, "Class 2")
            student6 = Student(
                student_id=student6_id,
                first_name="Ayesha",
                last_name="Malik",
                date_of_birth=date(2016, 7, 25),
                gender=Gender.FEMALE,
                cnic_bform="12345-2222222-1",
                guardian_id=guardian3.id,
                admission_date=date(2026, 8, 1),
                class_grade="Class 2",
                section="B",
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=1500.0,  # Set to 1500
                fee_concession=500.0,
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=1500.0
            )
            db.add(student6)
            db.commit()
            
            print(f"   ✅ Malik Family created (Family ID: {family3_id})")
            print(f"   ✅ Usman Malik (ID: {student5_id}) - Class 4 - Rs. 1,500/month - Concession: Rs. 500")
            print(f"   ✅ Ayesha Malik (ID: {student6_id}) - Class 2 - Rs. 1,500/month - Concession: Rs. 500")
        else:
            print(f"   ✅ Malik Family already exists")
        
        # Create Family 4 (2 students) - BUTT FAMILY
        print("\n8. Creating Family 4 (Butt Family - 2 students)...")
        existing_guardian4 = db.query(Guardian).filter(Guardian.cnic == "12345-3333333-1").first()
        if not existing_guardian4:
            family4_id = id_generator.generate_family_id(db)
            
            guardian4 = Guardian(
                family_id=family4_id,
                guardian_name="Salman Butt",
                relationship="Father",
                cnic="12345-3333333-1",
                mobile_number="0300-3333333",
                email="butt@example.com",
                occupation="Doctor",
                monthly_income=100000.0,
                address="House 101, Street 5, F-7/2, Islamabad",
                permanent_address="House 101, Street 5, F-7/2, Islamabad",
                emergency_contact_name="Sana Butt",
                emergency_contact_number="0301-4444444"
            )
            db.add(guardian4)
            db.flush()
            
            # Student 7 - Class 8 (Fee: Rs. 1,500)
            student7_id = id_generator.generate_student_id(db, "Class 8")
            student7 = Student(
                student_id=student7_id,
                first_name="Bilal",
                last_name="Butt",
                date_of_birth=date(2011, 5, 20),
                gender=Gender.MALE,
                cnic_bform="12345-3333333-1",
                guardian_id=guardian4.id,
                admission_date=date(2026, 8, 1),
                class_grade="Class 8",
                section="A",
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=1500.0,  # Set to 1500
                fee_concession=500.0,
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=1500.0
            )
            db.add(student7)
            db.commit()
            
            # Student 8 - Class 1 (Fee: Rs. 1,500)
            student8_id = id_generator.generate_student_id(db, "Class 1")
            student8 = Student(
                student_id=student8_id,
                first_name="Hira",
                last_name="Butt",
                date_of_birth=date(2017, 9, 10),
                gender=Gender.FEMALE,
                cnic_bform="12345-4444444-1",
                guardian_id=guardian4.id,
                admission_date=date(2026, 8, 1),
                class_grade="Class 1",
                section="B",
                academic_status=StudentStatus.ACTIVE,
                monthly_tuition_fee=1500.0,  # Set to 1500
                fee_concession=500.0,
                fee_status=FeeStatus.PENDING,
                total_outstanding_amount=1500.0
            )
            db.add(student8)
            db.commit()
            
            print(f"   ✅ Butt Family created (Family ID: {family4_id})")
            print(f"   ✅ Bilal Butt (ID: {student7_id}) - Class 8 - Rs. 1,500/month - Concession: Rs. 500")
            print(f"   ✅ Hira Butt (ID: {student8_id}) - Class 1 - Rs. 1,500/month - Concession: Rs. 500")
        else:
            print(f"   ✅ Butt Family already exists")
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed successfully!")
        print("=" * 60)
        
        print("\n📋 Default Credentials:")
        print("   Super Admin: superadmin / Admin@123")
        print("   Admin:       admin / Admin@123")
        print("   Principal:   principal / Principal@123")
        
        print("\n📋 Sample Students:")
        print("   Family 1 (Ahmed):")
        print(f"   Family ID: {guardian1.family_id}")
        print("   Ali Ahmed - Class 5 - Rs. 1,500/month - Concession: Rs. 500 (Net: Rs. 1,000)")
        print("   Sara Ahmed - Class 3 - Rs. 1,500/month - Concession: Rs. 500 (Net: Rs. 1,000)")
        print("   Family 2 (Khan):")
        print(f"   Family ID: {guardian2.family_id}")
        print("   Hamza Khan - Class 7 - Rs. 1,500/month - Concession: Rs. 500 (Net: Rs. 1,000)")
        print("   Zainab Khan - Class 6 - Rs. 1,500/month - Concession: Rs. 500 (Net: Rs. 1,000)")
        print("   Family 3 (Malik):")
        print(f"   Family ID: {guardian3.family_id}")
        print("   Usman Malik - Class 4 - Rs. 1,500/month - Concession: Rs. 500 (Net: Rs. 1,000)")
        print("   Ayesha Malik - Class 2 - Rs. 1,500/month - Concession: Rs. 500 (Net: Rs. 1,000)")
        print("   Family 4 (Butt):")
        print(f"   Family ID: {guardian4.family_id}")
        print("   Bilal Butt - Class 8 - Rs. 1,500/month - Concession: Rs. 500 (Net: Rs. 1,000)")
        print("   Hira Butt - Class 1 - Rs. 1,500/month - Concession: Rs. 500 (Net: Rs. 1,000)")
        print("   Total per family: Rs. 2,000 (2 students x Rs. 1,000)")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()