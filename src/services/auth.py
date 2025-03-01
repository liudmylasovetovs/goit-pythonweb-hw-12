"""
This module provides authentication and authorization services.

It includes password hashing, JWT token generation, user authentication,
and email verification token management.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional
import redis
from redis_lru import RedisLRU

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.database.models import User, UserRole


client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client, default_ttl=15 * 60)

class Hash:
    """
    Provides password hashing and verification methods.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain password against a hashed password.
        
        Args:
            plain_password (str): The plain text password.
            hashed_password (str): The hashed password.
        
        Returns:
            bool: True if passwords match, otherwise False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hashes a password using bcrypt.
        
        Args:
            password (str): The plain text password.
        
        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

oauth2_scheme = HTTPBearer()

async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Generates a new JWT access token.
    
    Args:
        data (dict): The payload data to encode.
        expires_delta (Optional[int]): The expiration time in seconds.
    
    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Retrieves the current authenticated user from the JWT token.
    
    Args:
        token (HTTPAuthorizationCredentials): The Bearer token credentials.
        db (Session): The database session dependency.
    
    Returns:
        User: The authenticated user.
    
    Raises:
        HTTPException: If token validation fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # user_service = UserService(db)
    # user = await user_service.get_user_by_username(username)
    # if user is None:
    #     raise credentials_exception
    # return user

    cache_key = f"user:{username}"
    cached_user = cache.get(cache_key)
    if cached_user:
        return cached_user

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)

    if user is None:
        raise credentials_exception
    cache.set(cache_key, user)

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user does not have enough privileges")
    return current_user


def create_email_token(data: dict) -> str:
    """
    Creates a JWT token for email verification.
    
    Args:
        data (dict): The payload data to encode.
    
    Returns:
        str: The encoded email verification token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

async def get_email_from_token(token: str) -> str:
    """
    Extracts the email from a JWT token.
    
    Args:
        token (str): The JWT token.
    
    Returns:
        str: The extracted email.
    
    Raises:
        HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token for email verification",
        )
