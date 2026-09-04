import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.models import SessionLocal, FeeChallan, Student, Guardian
from app.services.fee_service import FeeService

# Month order map for verification
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

print("=" * 60)
print("DEBUGGING ARREARS CALCULATION")
print("=" * 60)

# 1. Open database
db = SessionLocal()
fee_service = FeeService(db)

# 2. Get ALL challans from database
all_challans = db.query(FeeChallan).all()
print(f"\nTotal Challans in DB: {len(all_challans)}")
for c in all_challans:
    print(f"  - {c.bill_id} | Family: {c.family_id} | Month: {c.challan_month} | Remaining: {c.remaining_amount}")

# 3. Simulate generating for March (the problem month)
print(f"\n--- SIMULATING FEBRUARY CHALLAN GENERATION ---")
families = db.query(Guardian).all()
for family in families:
    family_id = family.family_id
    students = db.query(Student).filter(Student.guardian_id == family.id).all()
    
    # Calculate using the service method
    arrears_for_family = fee_service.get_family_outstanding_amount_for_month(family_id, "February")
    arrears_per_student = sum(fee_service.get_student_outstanding_amount(s.id, "February") for s in students)
    
    print(f"\nFamily: {family_id} (Students: {len(students)})")
    print(f"  Method 1 (Family-level): {arrears_for_family}")  # Should be 1000
    print(f"  Method 2 (Per-student sum): {arrears_per_student}")  # Should ALSO be 1000 if correct

    # Calculate using the UI cache logic
    cache_arrears = 0
    for challan in all_challans:
        if challan.family_id == family_id:
            challan_month_num = month_order.get(challan.challan_month, 1)
            if challan_month_num < 2:  # February = 2
                cache_arrears += challan.remaining_amount
    print(f"  Method 3 (UI Cache Logic): {cache_arrears}")  # Should be 1000

    # Calculate using the service create_challan logic
    # (Simulate what create_challan does)
    total_arrears = fee_service.get_family_outstanding_amount_for_month(family_id, "March")
    print(f"  Method 4 (For March): {total_arrears}")  # Should be 2000

print("\n" + "=" * 60)
print("DEBUG COMPLETE - You can now share the output")
print("=" * 60)

db.close()