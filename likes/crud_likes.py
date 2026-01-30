from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import insert, select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from database_files.database import post_likes_table, comment_likes_table, post_table, comment_table
from database_files.db_session import get_session

router = APIRouter(
    tags=['Likes'],
    prefix='/likes'
)


@router.post('/post/like/{user_id}/{post_id}')
async def like_post(user_id: int, post_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt_check_post = select(post_table).where(post_table.c.id == post_id)
    result = await session.execute(stmt_check_post)
    post_exists = result.fetchone()

    if not post_exists:
        raise HTTPException(status_code=404, detail=f'Post with id {post_id} not found')

    stmt_check_like = select(post_likes_table).where(
        (post_likes_table.c.post_id == post_id) &
        (post_likes_table.c.user_id == user_id)
    )

    result = await session.execute(stmt_check_like)
    existing_like = result.fetchone()

    if existing_like:
        raise HTTPException(status_code=400, detail='You already liked this post')

    stmt = insert(post_likes_table).values(
        post_id=post_id,
        user_id=user_id
    )
    await session.execute(stmt)
    await session.commit()
    return {'message': 'Post liked successfully'}


@router.delete('/post/unlike/{user_id}/{post_id}')
async def unlike_post(user_id: int, post_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = delete(post_likes_table).where(
        (post_likes_table.c.post_id == post_id) &
        (post_likes_table.c.user_id == user_id)
    )
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='Like not found')
    
    return {'message': 'Post unliked successfully'}


@router.get('/post/count')
async def get_post_likes_count(post_id: int, user_id: int = None, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(func.count()).select_from(post_likes_table).where(
        post_likes_table.c.post_id == post_id
    )
    count = await session.execute(stmt)
    count = count.scalar()

    is_liked = False
    if user_id:
        stmt_check = select(post_likes_table).where(
            (post_likes_table.c.post_id == post_id) &
            (post_likes_table.c.user_id == user_id)
        )
        result = await session.execute(stmt_check)
        is_liked = result.fetchone() is not None
    
    return {'post_id': post_id, 'likes_count': count, 'is_liked': is_liked}


@router.post('/comment/like/{user_id}/{comment_id}')
async def like_comment(user_id: int, comment_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt_check_comment = select(comment_table).where(comment_table.c.id == comment_id)
    result = await session.execute(stmt_check_comment)
    comment_exists = result.fetchone()

    if not comment_exists:
        raise HTTPException(status_code=404, detail=f'Comment with id {comment_id} not found')

    stmt_check_like = select(comment_likes_table).where(
        (comment_likes_table.c.comment_id == comment_id) &
        (comment_likes_table.c.user_id == user_id)
    )
    result = await session.execute(stmt_check_like)
    existing_like = result.fetchone()
    
    if existing_like:
        raise HTTPException(status_code=400, detail='You already liked this comment')
    
    stmt = insert(comment_likes_table).values(
        comment_id=comment_id,
        user_id=user_id
    )
    await session.execute(stmt)
    await session.commit()
    return {'message': 'Comment liked successfully'}


@router.delete('/comment/unlike/{user_id}/{comment_id}')
async def unlike_comment(user_id: int, comment_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = delete(comment_likes_table).where(
        (comment_likes_table.c.comment_id == comment_id) &
        (comment_likes_table.c.user_id == user_id)
    )
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='Like not found')
    
    return {'message': 'Comment unliked successfully'}


@router.get('/comment/count')
async def get_comment_likes_count(comment_id: int, user_id: int = None, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(func.count()).select_from(comment_likes_table).where(
        comment_likes_table.c.comment_id == comment_id
    )
    result = await session.execute(stmt)
    count = result.scalar()
    
    is_liked = False

    if user_id:
        stmt_check = select(comment_likes_table).where(
            (comment_likes_table.c.comment_id == comment_id) &
            (comment_likes_table.c.user_id == user_id)
        )
        result = await session.execute(stmt_check)
        is_liked = result.fetchone() is not None
    
    return {'comment_id': comment_id, 'likes_count': count, 'is_liked': is_liked}
