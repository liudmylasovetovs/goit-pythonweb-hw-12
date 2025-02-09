"""
This module defines routes for managing user contacts and utility functions.

It includes endpoints for creating, reading, updating, and deleting contacts,
searching for contacts, retrieving upcoming birthdays, and checking database health.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db

router = APIRouter(tags=["utils"])

@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Checks the health of the database connection.
    
    Args:
        db (AsyncSession): Database session dependency.
    
    Returns:
        dict: A message indicating the health status of the database.
    
    Raises:
        HTTPException: If the database connection is not configured correctly or an error occurs.
    """
    try:
        # Execute an asynchronous query
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": messages.HEALTHCHECKER_MESSAGE}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        ) from e
