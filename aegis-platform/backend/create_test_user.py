#!/usr/bin/env python3
"""Create test user for Playwright testing"""

import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models.user import User, Role
from passlib.context import CryptContext
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Create the test user that Playwright expects"""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if admin role exists, create if not
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(
                name="Admin",
                description="Full system access",
                permissions=json.dumps([
                    "read_all", "write_all", "delete_all", "manage_users", 
                    "manage_settings", "manage_integrations"
                ])
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
        
        # Check if test user exists
        existing_user = db.query(User).filter(
            User.email == "admin@aegis-platform.com"
        ).first()
        
        if existing_user:
            print("✅ Test user already exists: admin@aegis-platform.com")
            return
        
        # Create the test user with expected credentials
        test_user = User(
            username="admin",
            email="admin@aegis-platform.com",
            full_name="Test Administrator",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            is_verified=True,
            role_id=admin_role.id
        )
        
        db.add(test_user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print("   Email: admin@aegis-platform.com")
        print("   Password: admin123")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()