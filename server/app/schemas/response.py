from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ErrorDetail(BaseModel):
    """Pydantic model representing detailed error context."""
    code: str
    message: str
    details: Optional[Any] = None

class APIResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper that enforces a consistent JSON structure.
    All successful responses have success=True and data populated.
    All error responses have success=False and error details populated.
    """
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None
