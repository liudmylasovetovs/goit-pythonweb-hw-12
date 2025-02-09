"""
This module defines the UserService, which provides business logic for managing users.

It interacts with the UserRepository to perform user creation, retrieval,
and updating operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas.users import UserCreate

class UserService:
    """
    Service layer for managing user-related operations.
    """
    def __init__(self, db: AsyncSession):
        """
        Initializes the UserService with a database session.
        
        Args:
            db (AsyncSession): The database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user and assigns a Gravatar avatar if available.
        
        Args:
            body (UserCreate): The user creation data.
        
        Returns:
            User: The newly created user object.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieves a user by their ID.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            User | None: The user object if found, otherwise None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieves a user by their username.
        
        Args:
            username (str): The username of the user.
        
        Returns:
            User | None: The user object if found, otherwise None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieves a user by their email address.
        
        Args:
            email (str): The email address of the user.
        
        Returns:
            User | None: The user object if found, otherwise None.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str) -> None:
        """
        Marks a user's email as confirmed.
        
        Args:
            email (str): The email address of the user to confirm.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Updates the avatar URL for a user.
        
        Args:
            email (str): The email address of the user.
            url (str): The new avatar URL.
        
        Returns:
            User: The updated user object.
        """
        return await self.repository.update_avatar_url(email, url)

