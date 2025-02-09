"""
This module defines routes for managing user contacts.

It includes endpoints for creating, reading, updating, and deleting contacts,
searching for contacts, and retrieving upcoming birthdays.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.database.models import User
from src.schemas.contacts import ContactBase, ContactBirthdayRequest, ContactResponse
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK)
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieves a list of contacts for the authenticated user.
    
    Args:
        skip (int): Number of contacts to skip.
        limit (int): Maximum number of contacts to return.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.
    
    Returns:
        List[ContactResponse]: A list of contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieves a specific contact by ID.
    
    Args:
        contact_id (int): ID of the contact to retrieve.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.
    
    Returns:
        ContactResponse: The requested contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactBase,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Creates a new contact for the authenticated user.
    
    Args:
        body (ContactBase): Contact data.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.
    
    Returns:
        ContactResponse: The created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactBase,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Updates an existing contact.
    
    Args:
        body (ContactBase): Updated contact data.
        contact_id (int): ID of the contact to update.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.
    
    Returns:
        ContactResponse: The updated contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Deletes a contact by ID.
    
    Args:
        contact_id (int): ID of the contact to delete.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return

@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    text: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Searches contacts by name or other fields.
    
    Args:
        text (str): Search query.
        skip (int): Number of contacts to skip.
        limit (int): Maximum number of contacts to return.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.
    
    Returns:
        List[ContactResponse]: A list of matching contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(text, skip, limit, user)
    return contacts

@router.post("/upcoming-birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(
    body: ContactBirthdayRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieves contacts with upcoming birthdays within a given number of days.
    
    Args:
        body (ContactBirthdayRequest): Number of days to check for upcoming birthdays.
        db (AsyncSession): Database session dependency.
        user (User): The authenticated user.
    
    Returns:
        List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.upcoming_birthdays(body.days, user)
    return contacts
