"""
Test authentication system
"""

from app.database.models import SessionLocal
from app.utils.auth import Authentication, UserRole

def test_authentication():
    """Test the authentication system"""
    
    db = SessionLocal()
    auth = Authentication(db)
    
    print("=" * 60)
    print("Testing Authentication System")
    print("=" * 60)
    
    # Test 1: Login with super admin
    print("\n1. Testing Super Admin Login...")
    result = auth.login("superadmin", "Admin@123")
    if result["success"]:
        print(f"   ✅ {result['message']}")
        print(f"   User: {result['user'].username}")
        print(f"   Role: {result['user'].role.value}")
    else:
        print(f"   ❌ {result['message']}")
    
    # Test 2: Create an Admin user
    print("\n2. Creating Admin user...")
    result = auth.create_user(
        username="admin",
        password="Admin@123",
        email="superAdmin1@superscholars.com",
        full_name="Soban Arshad",
        role=UserRole.ADMIN
    )
    if result["success"]:
        print(f"   ✅ {result['message']}")
    else:
        print(f"   ❌ {result['message']}")
    
    # Test 3: Create a Principal user
    print("\n3. Creating Principal user...")
    result = auth.create_user(
        username="principal1",
        password="Principal@123",
        email="principal1@superscholars.com",
        full_name="Principal One",
        role=UserRole.PRINCIPAL
    )
    if result["success"]:
        print(f"   ✅ {result['message']}")
    else:
        print(f"   ❌ {result['message']}")
    
    # Test 4: Login with admin
    print("\n4. Testing Admin Login...")
    result = auth.login("admin1", "Admin@123")
    if result["success"]:
        print(f"   ✅ {result['message']}")
        print(f"   User: {result['user'].username}")
        print(f"   Role: {result['user'].role.value}")
    else:
        print(f"   ❌ {result['message']}")
    
    # Test 5: Wrong password
    print("\n5. Testing Wrong Password...")
    result = auth.login("admin1", "wrongpassword")
    if not result["success"]:
        print(f"   ✅ Correctly rejected: {result['message']}")
    else:
        print(f"   ❌ Should have failed!")
    
    # Test 6: Duplicate user
    print("\n6. Testing Duplicate User Creation...")
    result = auth.create_user(
        username="admin1",
        password="Admin@123",
        email="admin2@superscholars.com",
        full_name="Admin Two",
        role=UserRole.ADMIN
    )
    if not result["success"]:
        print(f"   ✅ Correctly rejected: {result['message']}")
    else:
        print(f"   ❌ Should have failed!")
    
    # Test 7: List all users
    print("\n7. Listing all users...")
    users = auth.list_all_users()
    for user in users:
        print(f"   - {user.username} ({user.role.value})")
    
    # Test 8: Logout
    print("\n8. Testing Logout...")
    result = auth.logout()
    if result["success"]:
        print(f"   ✅ {result['message']}")
    else:
        print(f"   ❌ {result['message']}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("✅ Authentication tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_authentication()