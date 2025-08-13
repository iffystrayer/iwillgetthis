from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    profile_picture: Optional[str] = None
    azure_ad_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str  # Can be username or email
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class TokenRefresh(BaseModel):
    refresh_token: str


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Optional[str] = None  # JSON string


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: Dict[str, List[str]] = {}
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_orm(cls, obj):
        # Convert permissions JSON string to structured format for frontend
        permissions = {}
        if obj.permissions:
            try:
                raw_permissions = json.loads(obj.permissions)
                if raw_permissions == ["all"]:
                    # Admin user with all permissions
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
                elif isinstance(raw_permissions, list):
                    # Convert list to module-based permissions
                    for perm in raw_permissions:
                        if "_" in perm:
                            module, action = perm.split("_", 1)
                            if module not in permissions:
                                permissions[module] = []
                            permissions[module].append(action)
                elif isinstance(raw_permissions, dict):
                    permissions = raw_permissions
            except (json.JSONDecodeError, ValueError):
                permissions = {}
        
        return cls(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            permissions=permissions,
            is_active=obj.is_active,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )
    
    class Config:
        from_attributes = True


class UserRoleAssignment(BaseModel):
    user_id: int
    role_id: int