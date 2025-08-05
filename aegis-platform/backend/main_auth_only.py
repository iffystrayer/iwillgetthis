from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Pydantic models for login
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app - NO DATABASE IMPORTS
app = FastAPI(
    title="Aegis Risk Management Platform - Auth Only",
    description="Minimal authentication service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:58533", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-only"}

@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    """Simple login endpoint for testing"""
    # Mock authentication - accept admin credentials
    if user_login.username == "admin@aegis-platform.com" and user_login.password == "admin123":
        mock_user = {
            "id": 1,
            "email": "admin@aegis-platform.com",
            "username": "admin",
            "full_name": "System Administrator",
            "is_active": True,
            "is_superuser": True,
            "roles": [
                {
                    "id": 1,
                    "name": "admin",
                    "description": "Administrator role",
                    "permissions": {
                        "dashboard": ["read", "write"],
                        "assets": ["read", "write", "delete"],
                        "risks": ["read", "write", "delete"],
                        "assessments": ["read", "write", "delete"],
                        "tasks": ["read", "write", "delete"],
                        "evidence": ["read", "write", "delete"],
                        "reports": ["read", "write"],
                        "ai_services": ["read", "write"],
                        "users": ["read", "write", "delete"],
                        "integrations": ["read", "write"],
                        "settings": ["read", "write"]
                    },
                    "is_active": True
                }
            ]
        }
        
        return Token(
            access_token="mock-access-token-123",
            refresh_token="mock-refresh-token-456",
            token_type="bearer",
            user=mock_user
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)