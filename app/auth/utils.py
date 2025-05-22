from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import config
from app.db.dynamodb import get_user_by_id

# Create OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

def create_access_token(data: dict) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()
    
    # Set expiration time
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Create JWT token
    encoded_jwt = jwt.encode(
        to_encode, 
        config.SECRET_KEY, 
        algorithm=config.ALGORITHM
    )
    
    return encoded_jwt

async def get_token_from_cookie(request: Request) -> Optional[str]:
    """Extract the JWT token from the cookie"""
    cookie_authorization = request.cookies.get("access_token")
    
    if not cookie_authorization:
        return None
        
    # Remove 'Bearer ' prefix if present
    if cookie_authorization.startswith("Bearer "):
        return cookie_authorization[7:]  # Skip 'Bearer ' prefix
    
    return cookie_authorization

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user based on JWT token.
    Returns None if no valid token is found.
    """
    # First try to get token from Authorization header via oauth2_scheme
    # If that fails, check the cookie
    if not token:
        token = await get_token_from_cookie(request)
        
    if not token:
        return None
        
    try:
        # Decode and validate the token
        payload = jwt.decode(
            token, 
            config.SECRET_KEY, 
            algorithms=[config.ALGORITHM]
        )
        
        # Extract user ID from token
        user_id = payload.get("sub")
        if user_id is None:
            return None
            
        # Get user from DynamoDB
        user = get_user_by_id(user_id)
        if not user:
            return None
            
        return user
        
    except JWTError:
        return None
