from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.core.config import settings
from app.core.exceptions import AuthenticationException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    verify_password,
)
from app.models.user import User
from app.repositories.token import token_repository
from app.repositories.user import user_repository
from app.schemas.auth import LoginRequest, TokenResponse

logger = structlog.get_logger()

class AuthService:
    """Service layer coordinating credential checks, JWT sessions, and token lifecycles."""
    
    async def authenticate_user(self, db: AsyncSession, login_in: LoginRequest) -> User:
        """Verifies user credentials (email & password). Checks account status."""
        user = await user_repository.get_by_email(db, email=login_in.email)
        if not user or not verify_password(login_in.password, user.password_hash):
            raise AuthenticationException("Incorrect email or password")
        if not user.is_active:
            raise AuthenticationException("User account is inactive")
        return user

    async def login_user(self, db: AsyncSession, user: User) -> TokenResponse:
        """Logs in a user, issuing token pairs and storing the hashed refresh token."""
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        # Securely hash and store the refresh token
        token_hash = hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await token_repository.create(
            db,
            obj_in={
                "user_id": user.id,
                "token_hash": token_hash,
                "expires_at": expires_at,
                "revoked": False,
            },
        )
        await db.commit()  # Commit transaction to ensure token storage persists

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def rotate_refresh_token(self, db: AsyncSession, refresh_token: str) -> TokenResponse:
        """Rotates a refresh token.
        Revokes the used token and issues a fresh Access/Refresh pair.
        Breach mitigation: If a revoked token is re-submitted, all active sessions for the user are immediately killed.
        """
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationException("Invalid or expired refresh token")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationException("Invalid token payload")

        user_id = uuid.UUID(user_id_str)
        token_hash = hash_token(refresh_token)

        # Lookup token in database
        db_token = await token_repository.get_by_hash(db, token_hash=token_hash)
        if not db_token:
            raise AuthenticationException("Refresh token is unregistered")

        # Breach Mitigation: Reuse of already revoked token
        if db_token.revoked:
            logger.warning(
                "Revoked refresh token reuse detected! Active breach mitigation: revoking all user sessions.",
                user_id=user_id,
                token_hash=token_hash,
            )
            await token_repository.revoke_all_for_user(db, user_id=user_id)
            await db.commit()
            raise AuthenticationException("Access denied: Session has already been rotated or invalidated")

        # Expiration Check
        # Convert expires_at to timezone-aware if needed for correct comparison
        expires_at = db_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            raise AuthenticationException("Refresh token has expired")

        # Successful Rotation: Revoke old token and issue fresh credentials
        db_token.revoked = True
        db.add(db_token)

        new_access_token = create_access_token(subject=user_id)
        new_refresh_token = create_refresh_token(subject=user_id)
        new_token_hash = hash_token(new_refresh_token)
        new_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await token_repository.create(
            db,
            obj_in={
                "user_id": user_id,
                "token_hash": new_token_hash,
                "expires_at": new_expires_at,
                "revoked": False,
            },
        )
        await db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    async def logout_user(self, db: AsyncSession, refresh_token: str) -> None:
        """Logs out a user session, revoking the supplied refresh token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationException("Invalid refresh token")

        token_hash = hash_token(refresh_token)
        db_token = await token_repository.get_by_hash(db, token_hash=token_hash)
        
        if db_token and not db_token.revoked:
            db_token.revoked = True
            db.add(db_token)
            await db.commit()

# Singleton service instance
auth_service = AuthService()
