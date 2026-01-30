from pydantic import BaseModel, Field, FilePath


class Post(BaseModel):
    post_name: str = Field(..., min_length=2, max_length=30)
    text: str = Field(..., min_length=5, max_length=3000)

