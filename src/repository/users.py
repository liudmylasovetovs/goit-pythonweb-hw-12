"""
This module defines the repository layer for managing user-related database operations.

It includes methods for retrieving, creating, updating, and confirming users.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserCreate

class UserRepository:
    """
    Repository for managing user-related database operations.
    """
    def __init__(self, session: AsyncSession):
        """
        Initializes the UserRepository with a database session.
        
        Args:
            session (AsyncSession): The database session.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieves a user by their ID.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            User | None: The user object if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieves a user by their username.
        
        Args:
            username (str): The username of the user.
        
        Returns:
            User | None: The user object if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieves a user by their email address.
        
        Args:
            email (str): The email address of the user.
        
        Returns:
            User | None: The user object if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Creates a new user in the database.
        
        Args:
            body (UserCreate): The user creation data.
            avatar (str, optional): The URL of the user's avatar.
        
        Returns:
            User: The newly created user object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def confirmed_email(self, email: str) -> None:
        """
        Marks a user's email as confirmed.
        
        Args:
            email (str): The email address of the user to confirm.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Updates the avatar URL for a user.
        
        Args:
            email (str): The email address of the user.
            url (str): The new avatar URL.
        
        Returns:
            User: The updated user object.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
