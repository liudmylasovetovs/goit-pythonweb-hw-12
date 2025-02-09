import json
from datetime import datetime, timedelta, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.services.email import send_email
from src.services.auth import Hash
from src.services.users import UserService
from src.conf.config import settings
from src.schemas.users import ResetPasswordRequest, SetNewPassword

router = APIRouter(prefix="/password", tags=["password"])


async def create_reset_token(email: str):
    """
    Generates a reset password token valid for 15 minutes.
    """
    expire = datetime.now(UTC) + timedelta(minutes=15)
    data = {"sub": email, "exp": expire}
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def verify_reset_token(token: str):
    """
    Verifies the reset password token and extracts the email.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


@router.post("/request-reset")
async def request_password_reset(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to request a password reset.

    Sends a reset token via email if the user exists.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found.",
        )

    reset_token = await create_reset_token(user.email)
    
    # Send email with reset token
    await send_email(
        to=user.email,
        subject="Password Reset Request",
        body=f"Click the link to reset your password: {settings.FRONTEND_URL}/reset-password?token={reset_token}",
    )

    return {"message": "If your email exists in our system, you will receive a password reset link shortly."}


@router.post("/reset")
async def reset_password(body: SetNewPassword, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to reset the password using the provided reset token.
    """
    email = await verify_reset_token(body.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token.",
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    # Hash the new password
    hashed_password = Hash().get_password_hash(body.new_password)
    user.hashed_password = hashed_password

    await db.commit()

    return {"message": "Password has been successfully reset."}
