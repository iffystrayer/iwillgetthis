"""
OAuth2/OIDC Provider Integration for Aegis Risk Management Platform
Supports multiple enterprise identity providers with automatic user provisioning
"""

import httpx
import jwt
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from urllib.parse import urlencode
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import json
import base64

from config import settings
from models.user import User, Role, UserRole
from auth import create_access_token, create_refresh_token


class OAuthProviderBase:
    """Base class for OAuth2/OIDC providers"""
    
    def __init__(self):
        self.client_id = ""
        self.client_secret = ""
        self.redirect_uri = ""
        self.scope = ""
        
    async def get_authorization_url(self, state: str) -> str:
        """Generate authorization URL for OAuth flow"""
        raise NotImplementedError
        
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
        
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from provider"""
        raise NotImplementedError
        
    def map_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map provider user data to our user model"""
        raise NotImplementedError


class AzureADProvider(OAuthProviderBase):
    """Microsoft Azure AD / Entra ID OAuth2 provider"""
    
    def __init__(self):
        super().__init__()
        self.client_id = settings.AZURE_CLIENT_ID
        self.client_secret = settings.AZURE_CLIENT_SECRET
        self.tenant_id = settings.AZURE_TENANT_ID
        self.redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/azure"
        self.scope = "openid profile email User.Read"
        
        # Azure AD endpoints
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.auth_endpoint = f"{self.authority}/oauth2/v2.0/authorize"
        self.token_endpoint = f"{self.authority}/oauth2/v2.0/token"
        self.userinfo_endpoint = "https://graph.microsoft.com/v1.0/me"
        
    async def get_authorization_url(self, state: str) -> str:
        """Generate Azure AD authorization URL"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": state,
            "response_mode": "query"
        }
        return f"{self.auth_endpoint}?{urlencode(params)}"
        
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for Azure AD token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {response.text}"
            )
            
        return response.json()
        
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Microsoft Graph"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.userinfo_endpoint, headers=headers)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info: {response.text}"
            )
            
        return response.json()
        
    def map_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map Azure AD user data to our user model"""
        return {
            "email": user_data.get("mail") or user_data.get("userPrincipalName"),
            "username": user_data.get("userPrincipalName"),
            "full_name": user_data.get("displayName"),
            "first_name": user_data.get("givenName"),
            "last_name": user_data.get("surname"),
            "department": user_data.get("department"),
            "job_title": user_data.get("jobTitle"),
            "phone": user_data.get("businessPhones", [None])[0],
            "external_id": user_data.get("id"),
            "provider": "azure_ad"
        }


class GoogleWorkspaceProvider(OAuthProviderBase):
    """Google Workspace OAuth2 provider"""
    
    def __init__(self):
        super().__init__()
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/google"
        self.scope = "openid profile email"
        
        # Google OAuth endpoints
        self.auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_endpoint = "https://oauth2.googleapis.com/token"
        self.userinfo_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"
        
    async def get_authorization_url(self, state: str) -> str:
        """Generate Google authorization URL"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        return f"{self.auth_endpoint}?{urlencode(params)}"
        
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for Google token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_endpoint, data=data)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {response.text}"
            )
            
        return response.json()
        
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.userinfo_endpoint, headers=headers)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info: {response.text}"
            )
            
        return response.json()
        
    def map_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map Google user data to our user model"""
        return {
            "email": user_data.get("email"),
            "username": user_data.get("email"),
            "full_name": user_data.get("name"),
            "first_name": user_data.get("given_name"),
            "last_name": user_data.get("family_name"),
            "external_id": user_data.get("id"),
            "provider": "google_workspace"
        }


class OktaProvider(OAuthProviderBase):
    """Okta OAuth2/OIDC provider"""
    
    def __init__(self):
        super().__init__()
        self.client_id = settings.OKTA_CLIENT_ID
        self.client_secret = settings.OKTA_CLIENT_SECRET
        self.domain = settings.OKTA_DOMAIN
        self.redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/okta"
        self.scope = "openid profile email"
        
        # Okta endpoints
        self.auth_endpoint = f"https://{self.domain}/oauth2/default/v1/authorize"
        self.token_endpoint = f"https://{self.domain}/oauth2/default/v1/token"
        self.userinfo_endpoint = f"https://{self.domain}/oauth2/default/v1/userinfo"
        
    async def get_authorization_url(self, state: str) -> str:
        """Generate Okta authorization URL"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": state
        }
        return f"{self.auth_endpoint}?{urlencode(params)}"
        
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for Okta token"""
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_endpoint, headers=headers, data=data)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {response.text}"
            )
            
        return response.json()
        
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Okta"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.userinfo_endpoint, headers=headers)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info: {response.text}"
            )
            
        return response.json()
        
    def map_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map Okta user data to our user model"""
        return {
            "email": user_data.get("email"),
            "username": user_data.get("preferred_username") or user_data.get("email"),
            "full_name": user_data.get("name"),
            "first_name": user_data.get("given_name"),
            "last_name": user_data.get("family_name"),
            "external_id": user_data.get("sub"),
            "provider": "okta"
        }


class OAuthService:
    """OAuth service for managing multiple providers"""
    
    def __init__(self):
        self.providers = {
            "azure_ad": AzureADProvider(),
            "google_workspace": GoogleWorkspaceProvider(),
            "okta": OktaProvider()
        }
        
    def get_provider(self, provider_name: str) -> OAuthProviderBase:
        """Get OAuth provider by name"""
        provider = self.providers.get(provider_name)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider_name}"
            )
        return provider
        
    async def create_or_update_user(self, user_data: Dict[str, Any], db: Session) -> User:
        """Create or update user from OAuth provider data"""
        
        # Check if user exists by email or external_id
        existing_user = db.query(User).filter(
            (User.email == user_data["email"]) |
            (User.external_id == user_data.get("external_id"))
        ).first()
        
        if existing_user:
            # Update existing user
            for key, value in user_data.items():
                if hasattr(existing_user, key) and value is not None:
                    setattr(existing_user, key, value)
            existing_user.last_login = datetime.utcnow()
            existing_user.is_active = True
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            # Create new user
            new_user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data.get("full_name"),
                department=user_data.get("department"),
                job_title=user_data.get("job_title"),
                phone=user_data.get("phone"),
                external_id=user_data.get("external_id"),
                provider=user_data.get("provider"),
                is_active=True,
                is_verified=True,
                created_via_sso=True,
                last_login=datetime.utcnow()
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Assign default role (e.g., ReadOnly for new SSO users)
            default_role = db.query(Role).filter(Role.name == "ReadOnly").first()
            if default_role:
                user_role = UserRole(user_id=new_user.id, role_id=default_role.id)
                db.add(user_role)
                db.commit()
                
            return new_user
            
    def generate_jwt_tokens(self, user: User) -> Dict[str, str]:
        """Generate JWT tokens for authenticated user"""
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "provider": user.provider}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


# Global OAuth service instance
oauth_service = OAuthService()