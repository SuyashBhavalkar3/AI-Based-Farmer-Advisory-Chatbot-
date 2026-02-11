#!/usr/bin/env python3
"""Initialize database and test setup."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def init_and_test():
    """Initialize database and run tests."""
    try:
        print("🔧 Initializing database...")
        from database.base import init_db
        init_db()
        print("✅ Database initialized successfully")
        
        print("\n🧪 Testing database connection...")
        from database.base import SessionLocal
        from database.models import User
        
        db = SessionLocal()
        try:
            # Test query
            count = db.query(User).count()
            print(f"✅ Database connection OK (Users: {count})")
        finally:
            db.close()
        
        print("\n🧪 Testing user creation...")
        from auth.auth_service import AuthService
        
        db = SessionLocal()
        try:
            # Clean up test user if exists
            db.query(User).filter(User.email == "test@test.com").delete()
            db.commit()
            
            # Create test user
            user = AuthService.signup(
                db,
                full_name="Test User",
                email="test@test.com",
                password="TestPass123!"
            )
            print(f"✅ User created successfully: {user.email} (ID: {user.id})")
            
            # Generate valid JWT token
            from auth.jwt_handler import create_access_token
            token = create_access_token(user.email)
            print(f"✅ JWT Token generated: {token[:50]}...")
            print(f"\n📋 Use this token in frontend:")
            print(f"   localStorage.setItem('access_token', '{token}')")
            
            # Verify user can be retrieved
            retrieved = db.query(User).filter(User.email == "test@test.com").first()
            if retrieved:
                print(f"✅ User retrieved successfully: {retrieved.full_name}")
            else:
                print("❌ Failed to retrieve user")
                return False
                
        finally:
            db.close()
        
        print("\n✅ All tests passed! Backend is ready.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_and_test()
    sys.exit(0 if success else 1)
