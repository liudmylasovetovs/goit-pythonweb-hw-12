"""
This module defines authentication routes for user registration, login, and email verification.

It includes endpoints for user registration, login, email verification requests,
and handling email confirmation.
"""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.users import RequestEmail, Token, User, UserCreate, UserLogin
from src.services.auth import Hash, create_access_token, get_email_from_token
from src.services.email import send_email
from src.services.users import UserService
from src.conf import messages

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Registers a new user and sends a confirmation email.
    
    Args:
        user_data (UserCreate): The user registration data.
        background_tasks (BackgroundTasks): Background task handler for sending emails.
        request (Request): The request object to get base URL.
        db (Session): The database session dependency.
    
    Returns:
        User: The newly created user object.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.API_ERROR_USER_ALREADY_EXIST,
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.API_ERROR_USER_ALREADY_EXIST,
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user

@router.post("/login", response_model=Token)
async def login_user(body: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns an access token.
    
    Args:
        body (UserLogin): The user login credentials.
        db (Session): The database session dependency.
    
    Returns:
        Token: An access token for the authenticated user.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user and not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.API_ERROR_USER_NOT_AUTHORIZED,
        )
    if not user or not Hash().verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.API_ERROR_WRONG_LOGIN_PASSWORD,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Requests email verification for an existing user.
    
    Args:
        body (RequestEmail): The email request payload.
        background_tasks (BackgroundTasks): Background task handler for sending emails.
        request (Request): The request object to get base URL.
        db (Session): The database session dependency.
    
    Returns:
        dict: A message indicating the status of email verification.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": messages.API_EMAIL_CONFIRMED}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation"}

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms the user's email using a token.
    
    Args:
        token (str): The email confirmation token.
        db (Session): The database session dependency.
    
    Returns:
        dict: A message indicating whether the email confirmation was successful.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": messages.API_EMAIL_CONFIRMED}
    await user_service.confirmed_email(email)
    return {"message": "Email successfully confirmed"}


