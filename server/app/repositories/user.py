from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    """Repository wrapping database operations for the User model."""
    
    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Fetches a User from the database using their unique email address."""
        query = select(self.model).where(self.model.email == email)
        result = await db.execute(query)
        return result.scalars().first()

# Singleton repository instance for ease of use across dependencies/services
user_repository = UserRepository()
