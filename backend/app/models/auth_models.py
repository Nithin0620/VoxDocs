"""
Pydantic models for authentication requests and responses.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class AuthUserResponse(BaseModel):
    id: str
    name: str
    email: str
    provider: str
    profilePic: Optional[str] = None
    createdAt: datetime


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: AuthUserResponse


class MeResponse(BaseModel):
    success: bool
    user: AuthUserResponse


class LogoutResponse(BaseModel):
    success: bool
    message: str