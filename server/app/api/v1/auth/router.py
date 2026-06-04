from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, AuthResponse
from app.schemas.user import UserCreate, UserResponse
from app.schemas.response import APIResponse
from app.services.auth import auth_service
from app.services.user import user_service

router = APIRouter()

@router.post(
    "/register",
    response_model=APIResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in: UserCreate, db: AsyncSession = Depends(get_db_session)
) -> APIResponse[AuthResponse]:
    """Registers a new User in LifeBase, auto-logs them in, and returns tokens with profile."""
    user = await user_service.create_user(db, user_in=user_in)
    tokens = await auth_service.login_user(db, user)
    user_data = UserResponse.model_validate(user)
    return APIResponse(
        success=True,
        data=AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            user=user_data,
        ),
    )

@router.post("/login", response_model=APIResponse[AuthResponse])
async def login(
    login_in: LoginRequest, db: AsyncSession = Depends(get_db_session)
) -> APIResponse[AuthResponse]:
    """Verifies user email/password, creates a new session, and returns tokens with profile."""
    user = await auth_service.authenticate_user(db, login_in=login_in)
    tokens = await auth_service.login_user(db, user)
    user_data = UserResponse.model_validate(user)
    return APIResponse(
        success=True,
        data=AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            user=user_data,
        ),
    )

@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh(
    refresh_in: RefreshRequest, db: AsyncSession = Depends(get_db_session)
) -> APIResponse[TokenResponse]:
    """Exchanges an active Refresh Token for new Access and Refresh tokens."""
    tokens = await auth_service.rotate_refresh_token(
        db, refresh_token=refresh_in.refresh_token
    )
    return APIResponse(success=True, data=tokens)

@router.post("/logout", response_model=APIResponse[dict])
async def logout(
    refresh_in: RefreshRequest, db: AsyncSession = Depends(get_db_session)
) -> APIResponse[dict]:
    """Invalidates the provided Refresh Token, terminating the user session."""
    await auth_service.logout_user(db, refresh_token=refresh_in.refresh_token)
    return APIResponse(success=True, data={"message": "Logged out successfully"})
