from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from database import get_db
from models.user import User, Role, UserRole
from models.audit import AuditLog
from schemas.user import (
    UserResponse, UserCreate, UserUpdate, RoleResponse, 
    RoleCreate, RoleUpdate, UserRoleAssignment
)
from auth import get_current_active_user, get_password_hash

router = APIRouter()


@router.get("/")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of users with pagination and filtering."""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.full_name.contains(search)) |
            (User.email.contains(search)) |
            (User.username.contains(search))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count for pagination
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    # Return paginated response structure expected by frontend
    return {
        "items": [UserResponse.model_validate(user) for user in users],
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/count")
async def get_users_count(
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get total count of users matching filters."""
    query = db.query(func.count(User.id))
    
    if search:
        query = query.filter(
            (User.full_name.contains(search)) |
            (User.email.contains(search)) |
            (User.username.contains(search))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    count = query.scalar()
    return {"count": count}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new user (Admin only)."""
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
        is_verified=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="user",
        entity_id=db_user.id,
        user_id=current_user.id,
        action="User created",
        description=f"User created by admin: {db_user.email}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Store old values for audit
    old_values = {
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active
    }
    
    # Update user fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="update",
        entity_type="user",
        entity_id=user.id,
        user_id=current_user.id,
        action="User updated",
        description=f"User updated: {user.email}",
        old_values=old_values,
        new_values=update_data,
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Soft delete user (set is_active=False)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user.is_active = False
    db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="delete",
        entity_type="user",
        entity_id=user.id,
        user_id=current_user.id,
        action="User deactivated",
        description=f"User deactivated: {user.email}",
        source="web_ui",
        risk_level="medium"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "User deactivated successfully"}


# Role management endpoints
@router.get("/roles/", response_model=List[RoleResponse])
async def get_roles(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all roles."""
    roles = db.query(Role).filter(Role.is_active == True).all()
    return roles


@router.post("/roles/", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new role (Admin only)."""
    # Check if role already exists
    existing_role = db.query(Role).filter(Role.name == role.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )
    
    db_role = Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    
    return db_role


@router.post("/assign-role")
async def assign_role(
    assignment: UserRoleAssignment,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Assign role to user."""
    # Check if user exists
    user = db.query(User).filter(User.id == assignment.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if role exists
    role = db.query(Role).filter(Role.id == assignment.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if assignment already exists
    existing_assignment = db.query(UserRole).filter(
        (UserRole.user_id == assignment.user_id) &
        (UserRole.role_id == assignment.role_id)
    ).first()
    
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this role"
        )
    
    # Create assignment
    user_role = UserRole(
        user_id=assignment.user_id,
        role_id=assignment.role_id,
        assigned_by=current_user.id
    )
    db.add(user_role)
    db.commit()
    
    return {"message": "Role assigned successfully"}