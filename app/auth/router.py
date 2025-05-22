from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import httpx
import json
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

from app.auth.utils import create_access_token, get_current_user
from app.db.dynamodb import get_user_by_email, create_user, update_user
import config

# Create router
auth_router = APIRouter()

# Set up templates
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page with Google auth button"""
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.get("/google")
async def login_google(request: Request):
    """Redirect to Google OAuth consent screen"""
    redirect_uri = f"{request.url.scheme}://{request.url.netloc}/auth"
    params = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": redirect_uri,
        "prompt": "select_account",
    }
    
    # Construct the authorization URL with params
    auth_url = f"{GOOGLE_AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    return RedirectResponse(url=auth_url)

@auth_router.get("/")
async def google_callback(request: Request, code: str = None):
    """Handle Google OAuth callback"""
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No authorization code provided"
        )
    
    # Exchange code for tokens
    redirect_uri = f"{request.url.scheme}://{request.url.netloc}/auth"
    token_data = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    
    async with httpx.AsyncClient() as client:
        # Get token
        token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get token: {token_response.text}"
            )
        
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        
        # Get user info
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = await client.get(GOOGLE_USERINFO_URL, headers=headers)
        
        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info: {userinfo_response.text}"
            )
        
        user_info = userinfo_response.json()
        
    # Get the user from the database or create a new one
    email = user_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google"
        )
    
    user = get_user_by_email(email)
    
    if not user:
        # Create new user
        user = {
            "id": str(uuid4()),
            "email": email,
            "name": user_info.get("name", ""),
            "picture": user_info.get("picture", ""),
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat()
        }
        create_user(user)
    else:
        # Update existing user
        user["last_login"] = datetime.now().isoformat()
        update_user(user)
    
    # Create access token
    token_data = {
        "sub": user["id"],
        "email": user["email"]
    }
    access_token = create_access_token(token_data)
    
    response = RedirectResponse(url="/dashboard")
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return response

@auth_router.get("/logout")
async def logout():
    """Log out the user by deleting the cookie"""
    response = RedirectResponse(url="/auth/login")
    response.delete_cookie(key="access_token")
    return response
