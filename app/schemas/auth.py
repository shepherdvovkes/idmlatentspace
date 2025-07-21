"""
Authentication schemas for IDM Latent Space
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    is_active: bool = True

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str
    confirm_password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """Schema for user response"""
    id: uuid.UUID
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None
    user_id: Optional[uuid.UUID] = None

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str
    confirm_password: str