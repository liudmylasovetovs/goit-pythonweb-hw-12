"""
This module defines the repository layer for managing contacts in the database.

It includes methods for creating, retrieving, updating, deleting, searching,
and retrieving upcoming birthdays of contacts associated with a user.
"""

from typing import List

from sqlalchemy import Integer, select, or_, and_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import timedelta

from src.database.models import Contact, User
from src.schemas.contacts import ContactResponse, ContactBase

class ContactRepository:
    """
    Repository for managing contact-related database operations.
    """
    def __init__(self, session: AsyncSession):
        """
        Initializes the ContactRepository with a database session.
        
        Args:
            session (AsyncSession): The database session.
        """
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Retrieves a list of contacts for a given user.
        
        Args:
            skip (int): Number of contacts to skip.
            limit (int): Maximum number of contacts to return.
            user (User): The authenticated user.
        
        Returns:
            List[Contact]: A list of contacts.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contacts_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieves a specific contact by ID.
        
        Args:
            contact_id (int): The ID of the contact.
            user (User): The authenticated user.
        
        Returns:
            Contact | None: The contact object if found, otherwise None.
        """
        stmt = select(Contact).filter_by(user=user, id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """
        Creates a new contact for the user.
        
        Args:
            body (ContactBase): The contact data.
            user (User): The authenticated user.
        
        Returns:
            Contact: The created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Deletes a contact by ID.
        
        Args:
            contact_id (int): The ID of the contact.
            user (User): The authenticated user.
        
        Returns:
            Contact | None: The deleted contact if found, otherwise None.
        """
        contact = await self.get_contacts_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """
        Updates an existing contact.
        
        Args:
            contact_id (int): The ID of the contact.
            body (ContactBase): The updated contact data.
            user (User): The authenticated user.
        
        Returns:
            Contact | None: The updated contact if found, otherwise None.
        """
        contact = await self.get_contacts_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
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
        stmt = (
            select(Contact)
            .filter(
                Contact.user == user,
                or_(
                    Contact.first_name.ilike(f"%{search}%"),
                    Contact.last_name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%"),
                    Contact.phone_number.ilike(f"%{search}%"),
                    Contact.additional_data.ilike(f"%{search}%"),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_upcoming_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Retrieves contacts with upcoming birthdays within a given number of days.
        
        Args:
            days (int): Number of days to check for upcoming birthdays.
            user (User): The authenticated user.
        
        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        today = func.current_date()
        future_date = today + timedelta(days=days)
        stmt = select(Contact).filter(
            Contact.user == user,
            or_(
                and_(
                    func.to_char(Contact.birthday, "MM-DD") >= func.to_char(today, "MM-DD"),
                    func.to_char(Contact.birthday, "MM-DD") <= func.to_char(future_date, "MM-DD")
                ),
                and_(
                    func.to_char(today, "MM-DD") > func.to_char(future_date, "MM-DD"),
                    or_(
                        func.to_char(Contact.birthday, "MM-DD") >= func.to_char(today, "MM-DD"),
                        func.to_char(Contact.birthday, "MM-DD") <= func.to_char(future_date, "MM-DD")
                    )
                )
            )
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
