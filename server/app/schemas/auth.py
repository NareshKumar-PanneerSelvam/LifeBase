from pydantic import BaseModel, EmailStr
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

