from better_profanity import profanity
from fastapi import HTTPException, APIRouter, Depends, Path, Form
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database_files.database import comment_table, post_table, user_table, reply_comments_table
from comments.models import CommentCreate, CommentUpdate
from database_files.db_session import get_session
from datetime import datetime

router = APIRouter(
    tags=['Comments'],
    prefix='/comments'
)

@router.post('/{post_id}/{user_id}')
async def create_comment(
    post_id: int, user_id: int, text: str = Form(...), session: AsyncSession = Depends(get_session)) -> dict:
    if profanity.contains_profanity(text):
        raise HTTPException(status_code=400, detail="Bad words are not allowed")

    result = await session.execute(select(post_table.c.id).where(post_table.c.id == post_id))
    post_exists = result.scalar_one_or_none()
    if not post_exists:
        raise HTTPException(status_code=404, detail=f'Post with id {post_id} not found')

    result = await session.execute(select(user_table.c.id).where(user_table.c.id == user_id))
    user_exists = result.scalar_one_or_none()
    if not user_exists:
        raise HTTPException(status_code=404, detail=f'User with id {user_id} not found')

    stmt = insert(comment_table).values(
        post_id=post_id,
        user_id=user_id,
        text=text,
        created_at=datetime.utcnow()
    )
    result = await session.execute(stmt)
    await session.commit()

    username_result = await session.execute(select(user_table.c.username).where(user_table.c.id == user_id))
    username = username_result.scalar_one()

    return {
        'id': result.lastrowid,
        'post_id': post_id,
        'user': username,
        'text': text,
        'created_at': datetime.utcnow().isoformat()
    }


@router.get('/post/{post_id}')
async def get_comments_by_post(post_id: int = Path(..., ge=1), session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(select(post_table.c.id).where(post_table.c.id == post_id))
    post_exists = result.scalar_one_or_none()
    if not post_exists:
        raise HTTPException(status_code=404, detail=f'Post with id {post_id} not found')

    stmt = select(comment_table, user_table.c.username).join(
        user_table, comment_table.c.user_id == user_table.c.id
    ).where(comment_table.c.post_id == post_id)
    
    results = await session.execute(stmt)
    rows = results.fetchall()

    if not rows:
        return {'message': 'No comments yet', 'comments': []}

    comments = []

    for row in rows:
        comments.append({
            'id': row[0],
            'post_id': row[1],
            'user_id': row[2],
            'user': row[5],
            'text': row[3],
            'created_at': row[4].isoformat()
        })

    return {'comments': comments}


@router.get('/{comment_id}')
async def get_comment(comment_id: int = Path(..., ge=1), session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(comment_table, user_table.c.username).join(
        user_table, comment_table.c.user_id == user_table.c.id
    ).where(comment_table.c.id == comment_id)
    
    result = await session.execute(stmt)
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f'Comment with id {comment_id} not found')

    return {
        'id': row[0],
        'post_id': row[1],
        'user': row[5],
        'text': row[3],
        'created_at': row[4].isoformat()
    }


@router.put('/{comment_id}')
async def update_comment(comment: CommentUpdate, session: AsyncSession = Depends(get_session)) -> dict:
    if profanity.contains_profanity(comment.text):
        raise HTTPException(status_code=400, detail="Bad words are not allowed")

    result = await session.execute(select(comment_table.c.id).where(comment_table.c.id == comment.id))
    comment_exists = result.scalar_one_or_none()
    if not comment_exists:
        raise HTTPException(status_code=404, detail=f'Comment with id {comment.id} not found')

    stmt = update(comment_table).where(comment_table.c.id == comment.id).values(text=comment.text)
    await session.execute(stmt)
    await session.commit()

    updated_result = await session.execute(
        select(comment_table, user_table.c.username).join(
            user_table, comment_table.c.user_id == user_table.c.id
        ).where(comment_table.c.id == comment.id)
    )
    updated = updated_result.fetchone()

    return {
        'id': updated[0],
        'post_id': updated[1],
        'user': updated[5],
        'text': updated[3],
        'created_at': updated[4].isoformat()
    }


@router.delete('/{comment_id}')
async def delete_comment(comment_id: int = Path(..., ge=1), session: AsyncSession = Depends(get_session)) -> dict:
    stmt = delete(comment_table).where(comment_table.c.id == comment_id)
    result = await session.execute(stmt)
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail=f'Comment with id {comment_id} not found')
    
    await session.commit()
    return {'message': f'Comment {comment_id} has been deleted'}


@router.post('/{comment_id}')
async def reply_comment(comment_id: int, reply: CommentCreate, session: AsyncSession = Depends(get_session)) -> dict:
    if profanity.contains_profanity(reply.text):
        raise HTTPException(status_code=400, detail="Bad words are not allowed")

    stmt_check_comment = select(comment_table).where(comment_table.c.id == comment_id)
    result = await session.execute(stmt_check_comment)
    comment_exists = result.fetchone()

    if comment_exists:
        stmt_add_comment_reply = insert(reply_comments_table).values(
            comment_id=comment_id,
            user_id=reply.user_id,
            text=reply.text,
            created_at=datetime.utcnow()
        )
        result = await session.execute(stmt_add_comment_reply)
        await session.commit()

        username_result = await session.execute(select(user_table.c.username).where(user_table.c.id == reply.user_id))
        username = username_result.scalar_one()

        return {
            'reply_comment_id': result.lastrowid,
            'parent_comment_id': comment_id,
            'user': username,
            'text': reply.text,
        }
    else:
        raise HTTPException(status_code=404, detail=f'Comment with id {comment_id} not found')


@router.get('/{comment_id}/replies')
async def get_comment_replies(comment_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(reply_comments_table, user_table.c.username).join(
        user_table, reply_comments_table.c.user_id == user_table.c.id
    ).where(reply_comments_table.c.comment_id == comment_id)

    result = await session.execute(stmt)
    rows = result.fetchall()

    if not rows:
        return {'message': 'No replies yet', 'replies': []}

    replies = []

    for row in rows:
        replies.append({
            'id': row[0],
            'comment_id': row[1],
            'user': row[5],
            'text': row[3],
            'created_at': row[4].isoformat()
        })

    return {'replies': replies}
