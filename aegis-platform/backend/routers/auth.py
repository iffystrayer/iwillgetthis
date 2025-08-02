from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models.user import User, Role, UserRole
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
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
        "user": user
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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user


@router.get("/verify-token")
async def verify_user_token(
    current_user: User = Depends(get_current_active_user)
):
    """Verify if the current token is valid."""
    return {"valid": True, "user_id": current_user.id, "email": current_user.email}