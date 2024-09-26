from pydantic import BaseModel, Field, SecretStr, EmailStr, field_validator
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    password: SecretStr = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr


class UpdateUser(BaseModel):
    new_username: Optional[str] = None
    old_email: EmailStr
    new_email: EmailStr
    old_password: SecretStr
    new_password: SecretStr
