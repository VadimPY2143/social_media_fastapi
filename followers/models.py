from pydantic import BaseModel


class Follow(BaseModel):
    follower_id: int
    following_id: int
