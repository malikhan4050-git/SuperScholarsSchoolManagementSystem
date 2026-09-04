"""
Authentication System for Super Scholars School Management System
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.models import User, UserRole, AuditLog

class PasswordManager:
    """Handle password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256 with salt
        """
        # Generate a random salt
        salt = secrets.token_hex(16)
        
        # Combine salt and password and hash
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        
        # Return salt + hash
        return f"{salt}${password_hash}"
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """
        Verify a password against the stored hash
        """
        try:
            # Split salt and hash
            salt, hash_value = stored_hash.split('$')
            
            # Recalculate hash
            new_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            
            # Compare
            return new_hash == hash_value
        except:
            return False

class Authentication:
    """Handle user authentication and session management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.current_user = None
    
    def create_user(self, username: str, password: str, email: str, full_name: str, role: UserRole) -> dict:
        """
        Create a new user (for Super Admin)
        """
        try:
            # Check if username already exists
            existing_user = self.db.query(User).filter(User.username == username).first()
            if existing_user:
                return {"success": False, "message": "Username already exists!"}
            
            # Check if email already exists
            existing_email = self.db.query(User).filter(User.email == email).first()
            if existing_email:
                return {"success": False, "message": "Email already exists!"}
            
            # Hash password
            hashed_password = PasswordManager.hash_password(password)
            
            # Create new user
            new_user = User(
                username=username,
                password_hash=hashed_password,
                email=email,
                full_name=full_name,
                role=role
            )
            
            self.db.add(new_user)
            self.db.commit()
            
            # Log the action
            self.log_action(f"Created user: {username} with role {role.value}")
            
            return {
                "success": True, 
                "message": f"User '{username}' created successfully!",
                "user": new_user
            }
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def login(self, username: str, password: str) -> dict:
        """
        Authenticate user login
        """
        try:
            # Find user
            user = self.db.query(User).filter(User.username == username).first()
            
            if not user:
                return {"success": False, "message": "Username not found!"}
            
            if not user.is_active:
                return {"success": False, "message": "Account is deactivated!"}
            
            # Verify password
            if PasswordManager.verify_password(password, user.password_hash):
                # Update last login
                user.last_login = datetime.now()
                self.db.commit()
                
                # Set current user
                self.current_user = user
                
                # Log login
                self.log_action(f"User '{username}' logged in")
                
                return {
                    "success": True,
                    "message": "Login successful!",
                    "user": user
                }
            else:
                # Log failed login attempt
                self.log_action(f"Failed login attempt for '{username}'")
                return {"success": False, "message": "Incorrect password!"}
                
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def logout(self):
        """
        Logout current user
        """
        if self.current_user:
            self.log_action(f"User '{self.current_user.username}' logged out")
            self.current_user = None
            return {"success": True, "message": "Logout successful!"}
        return {"success": False, "message": "No user is logged in!"}
    
    def get_current_user(self):
        """
        Get currently logged in user
        """
        return self.current_user
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> dict:
        """
        Change user password
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {"success": False, "message": "User not found!"}
            
            # Verify old password
            if not PasswordManager.verify_password(old_password, user.password_hash):
                return {"success": False, "message": "Current password is incorrect!"}
            
            # Update password
            user.password_hash = PasswordManager.hash_password(new_password)
            self.db.commit()
            
            # Log action
            self.log_action(f"User '{user.username}' changed password")
            
            return {"success": True, "message": "Password changed successfully!"}
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def deactivate_user(self, user_id: int) -> dict:
        """
        Deactivate a user account (for Super Admin)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {"success": False, "message": "User not found!"}
            
            user.is_active = False
            self.db.commit()
            
            # Log action
            self.log_action(f"Deactivated user '{user.username}'")
            
            return {"success": True, "message": f"User '{user.username}' deactivated!"}
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def activate_user(self, user_id: int) -> dict:
        """
        Activate a user account (for Super Admin)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {"success": False, "message": "User not found!"}
            
            user.is_active = True
            self.db.commit()
            
            # Log action
            self.log_action(f"Activated user '{user.username}'")
            
            return {"success": True, "message": f"User '{user.username}' activated!"}
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def list_all_users(self):
        """
        List all users (for Super Admin)
        """
        return self.db.query(User).all()
    
    def get_user_by_id(self, user_id: int):
        """
        Get user by ID
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def log_action(self, action: str, details: str = ""):
        """
        Log an action to audit log
        """
        try:
            log = AuditLog(
                user_id=self.current_user.id if self.current_user else None,
                action=action,
                details=details
            )
            self.db.add(log)
            self.db.commit()
        except:
            self.db.rollback()

class SuperAdminSetup:
    """Setup initial Super Admin account"""
    
    @staticmethod
    def create_super_admin(db: Session):
        """
        Create default Super Admin if not exists
        """
        # Check if super admin exists
        super_admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
        
        if super_admin:
            return {"success": True, "message": "Super Admin already exists"}
        
        # Create default super admin
        default_password = "Admin@123"  # Change this in production
        hashed_password = PasswordManager.hash_password(default_password)
        
        super_admin = User(
            username="superadmin",
            password_hash=hashed_password,
            email="superadmin@superscholars.com",
            full_name="System Super Admin",
            role=UserRole.SUPER_ADMIN
        )
        
        db.add(super_admin)
        db.commit()
        
        return {
            "success": True, 
            "message": "Default Super Admin created!",
            "credentials": {
                "username": "superadmin",
                "password": "Admin@123"
            }
        }