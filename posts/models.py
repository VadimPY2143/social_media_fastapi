from pydantic import BaseModel, Field


class Post(BaseModel):
    post_name: str = Field(..., min_length=2, max_length=25)
    text: str = Field(..., min_length=10)


class PostUpdate(BaseModel):
    post_name: str = Field(..., min_length=2, max_length=15)
    text: str = Field(..., min_length=10)
