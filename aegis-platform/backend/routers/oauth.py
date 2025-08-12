"""
OAuth2/OIDC Authentication Router for Aegis Risk Management Platform
Handles enterprise SSO integration with multiple providers
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import secrets
import json
from datetime import datetime, timedelta
try:
    import redis
except ImportError:
    redis = None

from database import get_db
from oauth_providers import oauth_service
from models.audit import AuditLog
from models.user import User
from schemas.user import UserResponse, Token
from auth import get_current_active_user
from config import settings

router = APIRouter()

# Redis client for state management
redis_client = redis.Redis.from_url(settings.REDIS_URL) if redis and hasattr(settings, 'REDIS_URL') else None


@router.get("/providers")
async def get_oauth_providers():
    """Get list of available OAuth providers"""
    return {
        "providers": [
            {
                "name": "azure_ad",
                "display_name": "Microsoft Azure AD",
                "enabled": bool(settings.AZURE_CLIENT_ID),
                "icon": "microsoft"
            },
            {
                "name": "google_workspace", 
                "display_name": "Google Workspace",
                "enabled": bool(getattr(settings, 'GOOGLE_CLIENT_ID', None)),
                "icon": "google"
            },
            {
                "name": "okta",
                "display_name": "Okta",
                "enabled": bool(getattr(settings, 'OKTA_CLIENT_ID', None)),
                "icon": "okta"
            }
        ]
    }


@router.get("/authorize/{provider}")
async def oauth_authorize(
    provider: str,
    redirect_url: Optional[str] = Query(None)
):
    """Initiate OAuth authorization flow"""
    
    # Validate provider
    oauth_provider = oauth_service.get_provider(provider)
    
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state and redirect URL in Redis for validation
    if redis_client:
        state_data = {
            "provider": provider,
            "redirect_url": redirect_url or "/dashboard",
            "timestamp": str(int(datetime.utcnow().timestamp()))
        }
        redis_client.setex(f"oauth_state:{state}", timedelta(minutes=10), json.dumps(state_data))
    
    # Get authorization URL from provider
    auth_url = await oauth_provider.get_authorization_url(state)
    
    return {"authorization_url": auth_url, "state": state}


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from provider"""
    
    # Check for authorization errors
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authorization failed: {error}"
        )
    
    # Validate state parameter
    if redis_client:
        state_data_json = redis_client.get(f"oauth_state:{state}")
        if not state_data_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OAuth state"
            )
        
        state_data = json.loads(state_data_json.decode())
        if state_data["provider"] != provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth state provider mismatch"
            )
        
        # Clean up state
        redis_client.delete(f"oauth_state:{state}")
        redirect_url = state_data.get("redirect_url", "/dashboard")
    else:
        redirect_url = "/dashboard"
    
    try:
        # Get OAuth provider
        oauth_provider = oauth_service.get_provider(provider)
        
        # Exchange authorization code for access token
        token_data = await oauth_provider.exchange_code_for_token(code)
        
        # Get user information from provider
        user_info = await oauth_provider.get_user_info(token_data["access_token"])
        
        # Map provider user data to our user model
        mapped_user_data = oauth_provider.map_user_data(user_info)
        
        # Create or update user in our database
        user = await oauth_service.create_or_update_user(mapped_user_data, db)
        
        # Generate our JWT tokens
        tokens = oauth_service.generate_jwt_tokens(user)
        
        # Log successful login
        audit_log = AuditLog(
            user_id=user.id,
            action="oauth_login",
            resource_type="auth",
            details=f"Successful OAuth login via {provider}",
            ip_address="unknown",  # You might want to extract this from request
            user_agent="oauth_callback"
        )
        db.add(audit_log)
        db.commit()
        
        # Return tokens (in production, you might want to set HTTP-only cookies instead)
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "provider": user.provider
            },
            "redirect_url": redirect_url
        }
        
    except Exception as e:
        # Log failed login attempt
        audit_log = AuditLog(
            action="oauth_login_failed",
            resource_type="auth",
            details=f"Failed OAuth login via {provider}: {str(e)}",
            ip_address="unknown",
            user_agent="oauth_callback"
        )
        db.add(audit_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@router.post("/link-account/{provider}")
async def link_oauth_account(
    provider: str,
    code: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Link an OAuth provider account to existing user"""
    
    try:
        # Get OAuth provider
        oauth_provider = oauth_service.get_provider(provider)
        
        # Exchange code for token
        token_data = await oauth_provider.exchange_code_for_token(code)
        
        # Get user info from provider
        user_info = await oauth_provider.get_user_info(token_data["access_token"])
        
        # Map user data
        mapped_user_data = oauth_provider.map_user_data(user_info)
        
        # Update current user with OAuth provider info
        current_user.external_id = mapped_user_data.get("external_id")
        current_user.provider = mapped_user_data.get("provider")
        
        # Update other fields if they're empty
        if not current_user.department and mapped_user_data.get("department"):
            current_user.department = mapped_user_data["department"]
        if not current_user.job_title and mapped_user_data.get("job_title"):
            current_user.job_title = mapped_user_data["job_title"]
        if not current_user.phone and mapped_user_data.get("phone"):
            current_user.phone = mapped_user_data["phone"]
            
        db.commit()
        db.refresh(current_user)
        
        # Log account linking
        audit_log = AuditLog(
            user_id=current_user.id,
            action="account_linked",
            resource_type="user",
            details=f"Linked {provider} account",
            ip_address="unknown"
        )
        db.add(audit_log)
        db.commit()
        
        return {"message": f"Successfully linked {provider} account"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to link account: {str(e)}"
        )


@router.delete("/unlink-account")
async def unlink_oauth_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlink OAuth provider from user account"""
    
    if not current_user.external_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OAuth account linked"
        )
    
    # Store provider info for logging
    provider = current_user.provider
    
    # Remove OAuth provider info
    current_user.external_id = None
    current_user.provider = None
    
    db.commit()
    
    # Log account unlinking
    audit_log = AuditLog(
        user_id=current_user.id,
        action="account_unlinked",
        resource_type="user",
        details=f"Unlinked {provider} account",
        ip_address="unknown"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": f"Successfully unlinked {provider} account"}


@router.get("/user-profile/{provider}")
async def get_oauth_user_profile(
    provider: str,
    access_token: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get user profile from OAuth provider (for profile syncing)"""
    
    try:
        # Get OAuth provider
        oauth_provider = oauth_service.get_provider(provider)
        
        # Get user info from provider
        user_info = await oauth_provider.get_user_info(access_token)
        
        # Map user data
        mapped_user_data = oauth_provider.map_user_data(user_info)
        
        return {
            "provider": provider,
            "profile": mapped_user_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user profile: {str(e)}"
        )