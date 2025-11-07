from pydantic import BaseModel


class PostLike(BaseModel):
    post_id: int
    user_id: int


class CommentLike(BaseModel):
    comment_id: int
    user_id: int
