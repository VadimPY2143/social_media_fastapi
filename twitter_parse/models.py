from pydantic import BaseModel, Field

class Tweet(BaseModel):
    query: str = Field(..., max_length=30)
    tweets: int = Field(10, ge=10)
    lang: str = Field("en", min_length=2, max_length=2)