from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    """Base schemas containing common fields for User data transfers."""
    email: EmailStr
    full_name: str
    role: str = "USER"

class UserCreate(UserBase):
    """Schema for registering a new user. Enforces strict password validation."""
    password: str = Field(..., min_length=8, max_length=128, description="Password must be at least 8 characters long")

class UserUpdate(BaseModel):
    """Schema for updating User profile attributes. All fields are optional."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Schema returned by endpoints when outputting user data. Enables ORM serialization."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
