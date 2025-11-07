from fastapi import HTTPException, APIRouter
from sqlalchemy import insert, select, delete, func
from sqlalchemy.orm import Session
from database import post_likes_table, comment_likes_table, post_table, comment_table, engine
from likes.models import PostLike, CommentLike


router = APIRouter(
    tags=['Likes'],
    prefix='/likes'
)


@router.post('/post/like')
def like_post(user_id: int, post_id: int) -> dict:
    with Session(engine) as session:
        stmt_check_post = select(post_table).where(post_table.c.id == post_id)
        post_exists = session.execute(stmt_check_post).fetchone()
        
        if not post_exists:
            raise HTTPException(status_code=404, detail=f'Post with id {post_id} not found')
        
        stmt_check_like = select(post_likes_table).where(
            (post_likes_table.c.post_id == post_id) & 
            (post_likes_table.c.user_id == user_id)
        )
        existing_like = session.execute(stmt_check_like).fetchone()
        
        if existing_like:
            raise HTTPException(status_code=400, detail='You already liked this post')
        
        stmt = insert(post_likes_table).values(
            post_id=post_id,
            user_id=user_id
        )
        session.execute(stmt)
        session.commit()
        return {'message': 'Post liked successfully'}


@router.delete('/post/unlike')
def unlike_post(user_id: int, post_id: int) -> dict:
    with Session(engine) as session:
        stmt = delete(post_likes_table).where(
            (post_likes_table.c.post_id == post_id) & 
            (post_likes_table.c.user_id == user_id)
        )
        result = session.execute(stmt)
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail='Like not found')
        
        session.commit()
        return {'message': 'Post unliked successfully'}


@router.get('/post/count')
def get_post_likes_count(post_id: int) -> dict:
    with Session(engine) as session:
        stmt = select(func.count()).select_from(post_likes_table).where(
            post_likes_table.c.post_id == post_id
        )
        count = session.execute(stmt).scalar()
        return {'post_id': post_id, 'likes_count': count}


@router.post('/comment/like')
def like_comment(user_id: int, comment_id: int) -> dict:
    with Session(engine) as session:
        stmt_check_comment = select(comment_table).where(comment_table.c.id == comment_id)
        comment_exists = session.execute(stmt_check_comment).fetchone()
        
        if not comment_exists:
            raise HTTPException(status_code=404, detail=f'Comment with id {comment_id} not found')
        
        stmt_check_like = select(comment_likes_table).where(
            (comment_likes_table.c.comment_id == comment_id) & 
            (comment_likes_table.c.user_id == user_id)
        )
        existing_like = session.execute(stmt_check_like).fetchone()
        
        if existing_like:
            raise HTTPException(status_code=400, detail='You already liked this comment')
        
        stmt = insert(comment_likes_table).values(
            comment_id=comment_id,
            user_id=user_id
        )
        session.execute(stmt)
        session.commit()
        return {'message': 'Comment liked successfully'}


@router.delete('/comment/unlike')
def unlike_comment(user_id: int, comment_id: int) -> dict:
    with Session(engine) as session:
        stmt = delete(comment_likes_table).where(
            (comment_likes_table.c.comment_id == comment_id) & 
            (comment_likes_table.c.user_id == user_id)
        )
        result = session.execute(stmt)
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail='Like not found')
        
        session.commit()
        return {'message': 'Comment unliked successfully'}


@router.get('/comment/count')
def get_comment_likes_count(comment_id: int) -> dict:
    with Session(engine) as session:
        stmt = select(func.count()).select_from(comment_likes_table).where(
            comment_likes_table.c.comment_id == comment_id
        )
        count = session.execute(stmt).scalar()
        return {'comment_id': comment_id, 'likes_count': count}
