import uuid
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db_session
from app.core.exceptions import AuthenticationException, ForbiddenException, NotFoundException
from app.core.security import decode_token
from app.models.user import User
from app.services.user import user_service

# Bearer security scheme configuration
security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token_auth: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> User:
    """Dependency resolver verifying access token JWTs and returning the authenticated User."""
    if not token_auth:
        raise AuthenticationException("Could not validate credentials: token missing")
        
    token = token_auth.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":

        raise AuthenticationException("Could not validate credentials or token expired")
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationException("Could not validate credentials: ID not specified")
    
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationException("Could not validate credentials: invalid ID structure")
        
    try:
        user = await user_service.get_user_by_id(db, user_id=user_id)
    except NotFoundException:
        raise AuthenticationException("User associated with this token does not exist")
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency resolver verifying that the authenticated user is active."""
    if not current_user.is_active:
        raise ForbiddenException("User account is inactive")
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency resolver verifying that the authenticated active user has ADMIN role."""
    if current_user.role.upper() != "ADMIN":
        raise ForbiddenException("Insufficient permissions: Admin access required")
    return current_user
