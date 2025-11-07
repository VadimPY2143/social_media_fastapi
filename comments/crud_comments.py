from better_profanity import profanity
from fastapi import HTTPException, APIRouter, Depends, Path
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session
from database import comment_table, engine, post_table, user_table
from comments.models import CommentCreate, CommentUpdate
from datetime import datetime

router = APIRouter(
    tags=['Comments'],
    prefix='/comments'
)

@router.post('/create/{post_id}/{user_id}')
async def create_comment(
    comment: CommentCreate = Depends()) -> dict:
    if profanity.contains_profanity(comment.text):
        raise HTTPException(status_code=400, detail="Bad words are not allowed")

    with Session(engine) as session:
        post_exists = session.execute(select(post_table.c.id).where(post_table.c.id == comment.post_id)).scalar_one_or_none()
        if not post_exists:
            raise HTTPException(status_code=404, detail=f'Post with id {comment.post_id} not found')

        user_exists = session.execute(select(user_table.c.id).where(user_table.c.id == comment.user_id)).scalar_one_or_none()
        if not user_exists:
            raise HTTPException(status_code=404, detail=f'User with id {comment.post_id} not found')

        stmt = insert(comment_table).values(
            post_id=comment.post_id,
            user_id=comment.user_id,
            text=comment.text,
            created_at=datetime.utcnow()
        )
        result = session.execute(stmt)
        session.commit()

        username = session.execute(select(user_table.c.username).where(user_table.c.id == comment.user_id)).scalar_one()

        return {
            'id': result.lastrowid,
            'post_id': comment.post_id,
            'user': username,
            'text': comment.text,
            'created_at': datetime.utcnow().isoformat()
        }


@router.get('/post/{post_id}')
def get_comments_by_post(post_id: int = Path(..., ge=1)) -> dict:
    with Session(engine) as session:
        post_exists = session.execute(select(post_table.c.id).where(post_table.c.id == post_id)).scalar_one_or_none()
        if not post_exists:
            raise HTTPException(status_code=404, detail=f'Post with id {post_id} not found')

        stmt = select(comment_table, user_table.c.username).join(
            user_table, comment_table.c.user_id == user_table.c.id
        ).where(comment_table.c.post_id == post_id)
        
        results = session.execute(stmt).fetchall()

        if not results:

            return {'message': 'No comments yet', 'comments': []}

        comments = []

        for row in results:
            comments.append({
                'id': row[0],
                'post_id': row[1],
                'user': row[5],
                'text': row[3],
                'created_at': row[4].isoformat()
            })

        return {'comments': comments}


@router.get('/{comment_id}')
def get_comment(comment_id: int = Path(..., ge=1)) -> dict:
    with Session(engine) as session:
        stmt = select(comment_table, user_table.c.username).join(
            user_table, comment_table.c.user_id == user_table.c.id
        ).where(comment_table.c.id == comment_id)
        
        result = session.execute(stmt).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail=f'Comment with id {comment_id} not found')

        return {
            'id': result[0],
            'post_id': result[1],
            'user': result[5],
            'text': result[3],
            'created_at': result[4].isoformat()
        }


@router.put('/update/{comment_id}')
def update_comment(comment: CommentUpdate = Depends()) -> dict:
    if profanity.contains_profanity(comment.text):
        raise HTTPException(status_code=400, detail="Bad words are not allowed")

    with Session(engine) as session:
        comment_exists = session.execute(select(comment_table.c.id).where(comment_table.c.id == comment.id)).scalar_one_or_none()
        if not comment_exists:
            raise HTTPException(status_code=404, detail=f'Comment with id {comment.id} not found')

        stmt = update(comment_table).where(comment_table.c.id == comment.id).values(text=comment.text)
        session.execute(stmt)
        session.commit()

        updated = session.execute(
            select(comment_table, user_table.c.username).join(
                user_table, comment_table.c.user_id == user_table.c.id
            ).where(comment_table.c.id == comment.id)
        ).fetchone()

        return {
            'id': updated[0],
            'post_id': updated[1],
            'user': updated[5],
            'text': updated[3],
            'created_at': updated[4].isoformat()
        }


@router.delete('/delete/{comment_id}')
def delete_comment(comment_id: int = Path(..., ge=1)) -> dict:
    with Session(engine) as session:
        stmt = delete(comment_table).where(comment_table.c.id == comment_id)
        result = session.execute(stmt)
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f'Comment with id {comment_id} not found')
        
        session.commit()
        return {'message': f'Comment {comment_id} has been deleted'}
