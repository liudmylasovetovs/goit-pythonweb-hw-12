from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from src.database.models import UserRole

# Схема користувача
class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

# Схема для запиту реєстрації
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str


# Схема для токену
class Token(BaseModel):
    access_token: str
    token_type: str

class RequestEmail(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    password: str
