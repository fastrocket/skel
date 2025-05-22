from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class UserBase(BaseModel):
    """Base user model with common attributes"""
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None

class UserCreate(UserBase):
    """Model for creating a new user"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: datetime = Field(default_factory=datetime.now)

class UserUpdate(BaseModel):
    """Model for updating a user"""
    name: Optional[str] = None
    picture: Optional[str] = None
    last_login: Optional[datetime] = None

class UserInDB(UserBase):
    """Model for a user stored in the database"""
    id: UUID
    created_at: datetime
    last_login: datetime

    class Config:
        orm_mode = True

class User(UserInDB):
    """Model for user response"""
    pass

class TokenData(BaseModel):
    """Model for JWT token data"""
    sub: str
    email: EmailStr
    exp: Optional[datetime] = None
