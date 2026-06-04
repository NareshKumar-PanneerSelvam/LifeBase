from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.config import settings
from app.core.exceptions import ForbiddenException, BadRequestException
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, AuthResponse, PromoteAdminRequest
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.response import APIResponse
from app.services.auth import auth_service
from app.services.user import user_service

router = APIRouter()

@router.post(
    "/promote-admin",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def promote_admin(
    promote_in: PromoteAdminRequest, db: AsyncSession = Depends(get_db_session)
) -> APIResponse[UserResponse]:
    """Promotes an existing user to ADMIN, or creates a new one as ADMIN.
    Guarded by settings.ADMIN_SECRET_KEY.
    """
    if promote_in.secret_key != settings.ADMIN_SECRET_KEY:
        raise ForbiddenException("Invalid administrative secret key.")
        
    user = await user_service.get_user_by_email(db, email=promote_in.email)
    if user:
        updated_user = await user_service.update_user(
            db, user_id=user.id, user_in=UserUpdate(role="ADMIN")
        )
        await db.commit()
        await db.refresh(updated_user)
        return APIResponse(success=True, data=UserResponse.model_validate(updated_user))
    
    if not promote_in.password or not promote_in.full_name:
        raise BadRequestException(
            "User does not exist. To create a new admin user, password and full_name are required."
        )
        
    new_user = await user_service.create_user(
        db,
        user_in=UserCreate(
            email=promote_in.email,
            password=promote_in.password,
            full_name=promote_in.full_name,
        ),
    )
    updated_user = await user_service.update_user(
        db, user_id=new_user.id, user_in=UserUpdate(role="ADMIN")
    )
    await db.commit()
    await db.refresh(updated_user)
    return APIResponse(success=True, data=UserResponse.model_validate(updated_user))

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
