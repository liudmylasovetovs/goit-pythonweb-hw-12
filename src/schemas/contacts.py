from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator



class ContactBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone_number: str = Field(min_length=6, max_length=20)
    birthday: date
    additional_data: Optional[str] = Field(max_length=150)

    @field_validator('birthday')
    def validate_birthday(cls, v):
        if v > date.today():
            raise ValueError('Birthday cannot be in the future')
        return v

class ContactResponse(ContactBase):
    id: int
    created_at: datetime | None
    updated_at: Optional[datetime] | None
   
    model_config = ConfigDict(from_attributes=True)


class ContactBirthdayRequest(BaseModel):
    days: int = Field(ge=0, le=366)
