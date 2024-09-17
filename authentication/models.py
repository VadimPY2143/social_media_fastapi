from pydantic import BaseModel, Field, SecretStr, EmailStr


class User(BaseModel):
    username: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    password: SecretStr


class UpdateUser(BaseModel):
    new_username: str
    old_email: str
    new_email: str
    old_password: str
    new_password: str
