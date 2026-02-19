from pydantic import BaseModel, Field, SecretStr, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    password: SecretStr = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    user_avatar: bool | None = None


class UpdateUser(BaseModel):
    new_username: Optional[str] = None
    new_email: Optional[EmailStr] = None
    old_password: SecretStr
    new_password: Optional[SecretStr] = None
