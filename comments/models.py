from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    post_id: int = Field(...)
    user_id: int = Field(...)
    text: str = Field(..., min_length=1, max_length=500)


class CommentUpdate(BaseModel):
    id: int = Field(...)
    text: str = Field(..., min_length=1, max_length=500)

