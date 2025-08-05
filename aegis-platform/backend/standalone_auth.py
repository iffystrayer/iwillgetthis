from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

app = FastAPI(title="Aegis Auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    if user_login.username == "admin@aegis-platform.com" and user_login.password == "admin123":
        return Token(
            access_token="token-123",
            refresh_token="refresh-456",
            user={
                "id": 1,
                "email": "admin@aegis-platform.com",
                "username": "admin",
                "full_name": "Admin",
                "is_active": True,
                "roles": [{"id": 1, "name": "admin"}]
            }
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")