from typing import Optional
import uuid
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.token import RefreshToken
from app.repositories.base import BaseRepository

class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository wrapping database operations for the RefreshToken model."""
    
    def __init__(self) -> None:
        super().__init__(RefreshToken)

    async def get_by_hash(self, db: AsyncSession, *, token_hash: str) -> Optional[RefreshToken]:
        """Fetches a RefreshToken entry using its unique SHA-256 hash representation."""
        query = select(self.model).where(self.model.token_hash == token_hash)
        result = await db.execute(query)
        return result.scalars().first()

    async def revoke_all_for_user(self, db: AsyncSession, *, user_id: uuid.UUID) -> None:
        """Revokes all active refresh tokens belonging to a specific user.
        Highly valuable during logout or token breach rotation routines.
        """
        query = (
            update(self.model)
            .where(self.model.user_id == user_id, self.model.revoked == False)
            .values(revoked=True)
        )
        await db.execute(query)

# Singleton repository instance
token_repository = RefreshTokenRepository()
