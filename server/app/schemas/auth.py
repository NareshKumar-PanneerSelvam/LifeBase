from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserResponse

class LoginRequest(BaseModel):
    """Schema containing user credentials for standard login flow."""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Schema containing issued Access and Refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AuthResponse(BaseModel):
    """Schema containing auth metadata, user details, and JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshRequest(BaseModel):
    """Schema containing the refresh token used to rotate credentials."""
    refresh_token: str

class PromoteAdminRequest(BaseModel):
    """Schema for promoting or creating an ADMIN user via secret key."""
    email: EmailStr
    secret_key: str
    password: Optional[str] = Field(None, min_length=8, max_length=128, description="Password if creating the admin user")
    full_name: Optional[str] = Field(None, description="Full name if creating the admin user")

