"""
This module defines the database models for users and contacts.

It includes the base model with timestamps and specific models for users and contacts.
"""

from datetime import date, datetime

from sqlalchemy import Boolean, Column, Integer, String, Table, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Date, DateTime

class Base(DeclarativeBase):
    """
    Base model that includes common timestamp fields.
    """
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

class Contact(Base):
    """
    Contact model representing a user's contact information.
    
    Attributes:
        id (int): Primary key identifier for the contact.
        first_name (str): Contact's first name.
        last_name (str): Contact's last name.
        email (str): Contact's email address.
        phone_number (str): Contact's phone number.
        birthday (date): Contact's birthday.
        additional_data (str, optional): Additional information about the contact.
        user_id (int): Foreign key referencing the associated user.
        user (User): Relationship to the User model.
    """
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    additional_data: Mapped[str] = mapped_column(String(150), nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")

class User(Base):
    """
    User model representing an application user.
    
    Attributes:
        id (int): Primary key identifier for the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        hashed_password (str): Hashed password for authentication.
        created_at (datetime): Timestamp of user creation.
        avatar (str, optional): URL or path to the user's avatar image.
        confirmed (bool): Indicates whether the user has confirmed their email.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
