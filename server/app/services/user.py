from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    """Service layer coordinating business logic operations for the User model."""
    
    async def get_user_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User:
        """Fetches a User by their ID. Raises NotFoundException if not present."""
        user = await user_repository.get(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Fetches a User by email. Returns None if not present."""
        return await user_repository.get_by_email(db, email=email)

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        """Creates a new User record, hashing their password before database insertion."""
        existing_user = await self.get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise BadRequestException("A user with this email already exists")

        user_data = user_in.model_dump()
        password = user_data.pop("password")
        user_data["password_hash"] = hash_password(password)

        user = await user_repository.create(db, obj_in=user_data)
        return user

    async def update_user(self, db: AsyncSession, user_id: uuid.UUID, user_in: UserUpdate) -> User:
        """Updates User attributes securely, re-hashing password if changed."""
        user = await self.get_user_by_id(db, user_id)
        
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            password = update_data.pop("password")
            update_data["password_hash"] = hash_password(password)

        if "email" in update_data and update_data["email"] != user.email:
            existing = await self.get_user_by_email(db, email=update_data["email"])
            if existing:
                raise BadRequestException("A user with this email already exists")

        updated_user = await user_repository.update(db, db_obj=user, obj_in=update_data)
        return updated_user

# Singleton service instance
user_service = UserService()
