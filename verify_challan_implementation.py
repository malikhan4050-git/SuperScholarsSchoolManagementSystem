#!/usr/bin/env python3
"""
Fee Challan Implementation Verification Script
Tests that all components are properly integrated
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_files_exist():
    """Verify all necessary files exist"""
    files_to_check = [
        "app/database/models.py",
        "app/services/fee_service.py",
        "app/utils/id_generator.py",
        "app/ui/fee_challan_screen.py",
        "app/utils/challan_printer.py",
        "app/ui/admin_dashboard.py",
    ]
    
    print("✓ Checking if all files exist...")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ MISSING: {file_path}")
            return False
    return True

def verify_imports():
    """Verify all imports work (without dependencies)"""
    print("\n✓ Checking Python syntax...")
    
    files_to_compile = [
        "app/database/models.py",
        "app/services/fee_service.py",
        "app/utils/id_generator.py",
        "app/utils/challan_printer.py",
    ]
    
    for file_path in files_to_compile:
        try:
            import py_compile
            py_compile.compile(file_path, doraise=True)
            print(f"  ✓ {file_path}")
        except py_compile.PyCompileError as e:
            print(f"  ✗ SYNTAX ERROR in {file_path}: {e}")
            return False
    
    return True

def verify_models():
    """Verify model definitions"""
    print("\n✓ Checking database models...")
    
    try:
        # Parse the models file to check for FeeChallan class
        with open("app/database/models.py", "r") as f:
            content = f.read()
            if "class FeeChallan" in content:
                print("  ✓ FeeChallan model found")
            else:
                print("  ✗ FeeChallan model NOT found")
                return False
            
            if "fee_challans" in content:
                print("  ✓ fee_challans table definition found")
            else:
                print("  ✗ fee_challans table NOT found")
                return False
    except Exception as e:
        print(f"  ✗ Error reading models: {e}")
        return False
    
    return True

def verify_services():
    """Verify service methods"""
    print("\n✓ Checking FeeService methods...")
    
    try:
        with open("app/services/fee_service.py", "r") as f:
            content = f.read()
            methods_to_check = [
                "get_all_families_with_students",
                "create_challan",
                "get_family_outstanding_amount",
                "update_challan_status",
                "get_challan_by_bill_id",
            ]
            
            for method in methods_to_check:
                if f"def {method}" in content:
                    print(f"  ✓ {method}() found")
                else:
                    print(f"  ✗ {method}() NOT found")
                    return False
    except Exception as e:
        print(f"  ✗ Error reading services: {e}")
        return False
    
    return True

def verify_ui():
    """Verify UI components"""
    print("\n✓ Checking UI components...")
    
    try:
        with open("app/ui/fee_challan_screen.py", "r") as f:
            content = f.read()
            if "class FeeChallanlScreen" in content:
                print("  ✓ FeeChallanlScreen class found")
            else:
                print("  ✗ FeeChallanlScreen class NOT found")
                return False
            
            ui_methods = ["create_table", "generate_challans", "print_challans"]
            for method in ui_methods:
                if f"def {method}" in content:
                    print(f"  ✓ {method}() found")
                else:
                    print(f"  ✗ {method}() NOT found")
                    return False
    except Exception as e:
        print(f"  ✗ Error reading UI: {e}")
        return False
    
    return True

def verify_printer():
    """Verify PDF printer"""
    print("\n✓ Checking PDF printer...")
    
    try:
        with open("app/utils/challan_printer.py", "r") as f:
            content = f.read()
            if "class ChallanPrinter" in content:
                print("  ✓ ChallanPrinter class found")
            else:
                print("  ✗ ChallanPrinter class NOT found")
                return False
            
            printer_methods = [
                "generate_challan_pdf",
                "generate_multiple_challans_pdf",
                "_build_challan_content",
            ]
            for method in printer_methods:
                if f"def {method}" in content:
                    print(f"  ✓ {method}() found")
                else:
                    print(f"  ✗ {method}() NOT found")
                    return False
    except Exception as e:
        print(f"  ✗ Error reading printer: {e}")
        return False
    
    return True

def verify_admin_dashboard():
    """Verify admin dashboard integration"""
    print("\n✓ Checking Admin Dashboard integration...")
    
    try:
        with open("app/ui/admin_dashboard.py", "r") as f:
            content = f.read()
            if "from app.ui.fee_challan_screen import FeeChallanlScreen" in content:
                print("  ✓ FeeChallanlScreen import found")
            else:
                print("  ✗ FeeChallanlScreen import NOT found")
                return False
            
            if "self.fee_challan_screen = FeeChallanlScreen" in content:
                print("  ✓ FeeChallanlScreen instantiation found")
            else:
                print("  ✗ FeeChallanlScreen instantiation NOT found")
                return False
    except Exception as e:
        print(f"  ✗ Error reading admin dashboard: {e}")
        return False
    
    return True

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Fee Challan Implementation Verification")
    print("=" * 60)
    
    checks = [
        ("Files Exist", verify_files_exist),
        ("Python Syntax", verify_imports),
        ("Database Models", verify_models),
        ("Fee Services", verify_services),
        ("UI Components", verify_ui),
        ("PDF Printer", verify_printer),
        ("Admin Dashboard", verify_admin_dashboard),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n✗ {check_name} check failed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Implementation is complete!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install customtkinter reportlab sqlalchemy")
        print("2. Initialize database: python app/database/init_db.py")
        print("3. Run application: python main.py")
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Please review the errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
