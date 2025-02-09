"""
This module defines the ContactService, which provides business logic for managing contacts.

It interacts with the ContactRepository to perform CRUD operations,
search contacts, and retrieve upcoming birthdays.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.database.models import User
from src.schemas.contacts import ContactBase, ContactResponse, ContactBirthdayRequest

class ContactService:
    """
    Service layer for managing contact-related operations.
    """
    def __init__(self, db: AsyncSession):
        """
        Initializes the ContactService with a database session.
        
        Args:
            db (AsyncSession): The database session.
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        """
        Creates a new contact for the authenticated user.
        
        Args:
            body (ContactBase): The contact data.
            user (User): The authenticated user.
        
        Returns:
            Contact: The created contact object.
        """
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Retrieves a list of contacts for the authenticated user.
        
        Args:
            skip (int): Number of contacts to skip.
            limit (int): Maximum number of contacts to return.
            user (User): The authenticated user.
        
        Returns:
            List[Contact]: A list of contacts.
        """
        return await self.contact_repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieves a specific contact by ID.
        
        Args:
            contact_id (int): The ID of the contact.
            user (User): The authenticated user.
        
        Returns:
            Contact | None: The requested contact if found, otherwise None.
        """
        return await self.contact_repository.get_contacts_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactBase, user: User):
        """
        Updates an existing contact.
        
        Args:
            contact_id (int): The ID of the contact.
            body (ContactBase): The updated contact data.
            user (User): The authenticated user.
        
        Returns:
            Contact | None: The updated contact if found, otherwise None.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Deletes a contact by ID.
        
        Args:
            contact_id (int): The ID of the contact.
            user (User): The authenticated user.
        
        Returns:
            Contact | None: The deleted contact if found, otherwise None.
        """
        return await self.contact_repository.remove_contact(contact_id, user)
    
    async def search_contacts(self, search: str, skip: int, limit: int, user: User):
        """
        Searches for contacts based on various fields.
        
        Args:
            search (str): The search query.
            skip (int): Number of contacts to skip.
            limit (int): Maximum number of contacts to return.
            user (User): The authenticated user.
        
        Returns:
            List[Contact]: A list of matching contacts.
        """
        return await self.contact_repository.search_contacts(search, skip, limit, user)
    
    async def get_upcoming_birthdays(self, days: int, user: User):
        """
        Retrieves contacts with upcoming birthdays within a given number of days.
        
        Args:
            days (int): Number of days to check for upcoming birthdays.
            user (User): The authenticated user.
        
        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        return await self.contact_repository.get_upcoming_birthdays(days, user)
