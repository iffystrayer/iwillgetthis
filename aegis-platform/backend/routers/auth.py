from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models.user import User, Role, UserRole
import json
from models.audit import AuditLog
from schemas.user import UserCreate, UserLogin, Token, TokenRefresh, UserResponse
from auth import (
    authenticate_user, create_access_token, create_refresh_token,
    get_password_hash, verify_token, get_current_user, get_current_active_user
)
from config import settings

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        department=user.department,
        job_title=user.job_title,
        phone=user.phone,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True  # In production, this should be False until email verification
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Assign default role (ReadOnly)
    default_role = db.query(Role).filter(Role.name == "ReadOnly").first()
    if default_role:
        user_role = UserRole(user_id=db_user.id, role_id=default_role.id)
        db.add(user_role)
        db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="user",
        entity_id=db_user.id,
        user_id=db_user.id,
        action="User registration",
        description=f"New user registered: {db_user.email}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_user


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return tokens."""
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        # Log failed login attempt
        audit_log = AuditLog(
            event_type="login_failed",
            entity_type="user",
            action="Failed login attempt",
            description=f"Failed login attempt for: {user_login.username}",
            source="web_ui",
            risk_level="medium"
        )
        db.add(audit_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Log successful login
    audit_log = AuditLog(
        event_type="login",
        entity_type="user",
        entity_id=user.id,
        user_id=user.id,
        action="User login",
        description=f"User logged in: {user.email}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    print("DEBUG: Starting role loading process")
    
    # Load user roles for the response
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    print(f"Debug: Found {len(user_roles)} user roles for user {user.id}")
    roles = []
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            print(f"Debug: Processing role {role.name} with permissions {role.permissions}")
            # Transform permissions for frontend
            permissions = {}
            if role.permissions:
                try:
                    raw_permissions = json.loads(role.permissions)
                    print(f"Debug: Raw permissions: {raw_permissions}")
                    if raw_permissions == ["all"]:
                        permissions = {
                            "assets": ["read", "write", "delete"],
                            "risks": ["read", "write", "delete"],
                            "assessments": ["read", "write", "delete"],
                            "tasks": ["read", "write", "delete"],
                            "evidence": ["read", "write", "delete"],
                            "reports": ["read", "write", "delete"],
                            "ai_services": ["read", "write", "delete"],
                            "integrations": ["read", "write", "delete"],
                            "users": ["read", "write", "delete"],
                            "settings": ["read", "write", "delete"]
                        }
                        print(f"Debug: Transformed permissions: {permissions}")
                except Exception as e:
                    print(f"Debug: Error parsing permissions: {e}")
                    permissions = {}
            
            role_data = {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": permissions,
                "is_active": role.is_active
            }
            roles.append(role_data)
            print(f"Debug: Added role data: {role_data}")
    
    # Add roles to user object
    user_dict = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "last_login": user.last_login,
        "profile_picture": user.profile_picture,
        "department": user.department,
        "job_title": user.job_title,
        "phone": user.phone,
        "azure_ad_id": user.azure_ad_id,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "roles": roles
    }
    print(f"Debug: Final user dict with roles: {user_dict['roles']}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
        "user": user_dict
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(token_refresh: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token_refresh.refresh_token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
        "user": user
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user."""
    # Log logout event
    audit_log = AuditLog(
        event_type="logout",
        entity_type="user",
        entity_id=current_user.id,
        user_id=current_user.id,
        action="User logout",
        description=f"User logged out: {current_user.email}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user information with roles."""
    print("DEBUG: Getting current user with roles")
    
    # Load user roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
    print(f"DEBUG: Found {len(user_roles)} roles for user")
    
    roles = []
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            print(f"DEBUG: Processing role {role.name}")
            # Transform permissions for frontend
            permissions = {}
            if role.permissions:
                try:
                    raw_permissions = json.loads(role.permissions)
                    if raw_permissions == ["all"]:
                        permissions = {
                            "assets": ["read", "write", "delete"],
                            "risks": ["read", "write", "delete"],
                            "assessments": ["read", "write", "delete"],
                            "tasks": ["read", "write", "delete"],
                            "evidence": ["read", "write", "delete"],
                            "reports": ["read", "write", "delete"],
                            "ai_services": ["read", "write", "delete"],
                            "integrations": ["read", "write", "delete"],
                            "users": ["read", "write", "delete"],
                            "settings": ["read", "write", "delete"]
                        }
                except:
                    permissions = {}
            
            role_data = {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": permissions,
                "is_active": role.is_active
            }
            roles.append(role_data)
    
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "last_login": current_user.last_login,
        "profile_picture": current_user.profile_picture,
        "department": current_user.department,
        "job_title": current_user.job_title,
        "phone": current_user.phone,
        "azure_ad_id": current_user.azure_ad_id,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "roles": roles
    }
    
    print(f"DEBUG: Returning user with {len(roles)} roles")
    return user_dict


@router.get("/verify-token")
async def verify_user_token(
    current_user: User = Depends(get_current_active_user)
):
    """Verify if the current token is valid."""
    return {"valid": True, "user_id": current_user.id, "email": current_user.email}