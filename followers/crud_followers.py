from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import insert, select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from database_files.database import followers_table, user_table
from followers.models import Follow
from database_files.db_session import get_session

router = APIRouter(
    tags=['Followers'],
    prefix='/followers'
)


@router.post('/follow')
async def follow_user(follow: Follow, session: AsyncSession = Depends(get_session)) -> dict:
    if follow.follower_id == follow.following_id:
        raise HTTPException(status_code=400, detail='You cannot follow yourself')
    
    stmt_check_user = select(user_table).where(user_table.c.id == follow.following_id)
    result = await session.execute(stmt_check_user)
    user_exists = result.fetchone()
    
    if not user_exists:
        raise HTTPException(status_code=404, detail=f'User with id {follow.following_id} not found')
    
    stmt_check_follow = select(followers_table).where(
        (followers_table.c.follower_id == follow.follower_id) &
        (followers_table.c.following_id == follow.following_id)
    )
    result = await session.execute(stmt_check_follow)
    existing_follow = result.fetchone()
    
    if existing_follow:
        raise HTTPException(status_code=400, detail='You already follow this user')
    
    stmt = insert(followers_table).values(
        follower_id=follow.follower_id,
        following_id=follow.following_id
    )
    await session.execute(stmt)
    await session.commit()

    username = user_exists[1]
    return {'message': f'You are now following {username}'}


@router.delete('/unfollow/{follower_id}/{following_id}')
async def unfollow_user(follower_id: int, following_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = delete(followers_table).where(
        (followers_table.c.follower_id == follower_id) & 
        (followers_table.c.following_id == following_id)
    )
    result = await session.execute(stmt)
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='Follow relationship not found')
    
    await session.commit()
    return {'message': f'You unfollowed user {following_id}'}


@router.get('/{user_id}')
async def get_followers(user_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(
        followers_table.c.follower_id,
        user_table.c.username).join(
        user_table,
        user_table.c.id == followers_table.c.follower_id).where(
        followers_table.c.following_id == user_id)
    
    result = await session.execute(stmt)
    rows = result.fetchall()
    followers = []
    for follower in rows:
        fol_info = {'id': follower[0],
                    'username': follower[1]}
        followers.append(fol_info)
    
    return {
        'user_id': user_id,
        'followers_count': len(followers),
        'followers': followers
    }


@router.get('/following/{user_id}')
async def get_following(user_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(
        followers_table.c.following_id,
        user_table.c.username
    ).join(
        user_table,
        user_table.c.id == followers_table.c.following_id
    ).where(
        followers_table.c.follower_id == user_id
    )
    
    result = await session.execute(stmt)
    rows = result.fetchall()
    
    following_list = [
        {'user_id': row[0], 'username': row[1]} 
        for row in rows
    ]
    
    return {
        'user_id': user_id,
        'following_count': len(following_list),
        'following': following_list
    }


@router.get('/stats/{user_id}')
async def get_follower_stats(user_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    followers_stmt = select(func.count()).select_from(followers_table).where(
        followers_table.c.following_id == user_id
    )
    result = await session.execute(followers_stmt)
    followers_count = result.scalar()
    
    following_stmt = select(func.count()).select_from(followers_table).where(
        followers_table.c.follower_id == user_id
    )
    result = await session.execute(following_stmt)
    following_count = result.scalar()
    
    return {
        'user_id': user_id,
        'followers': followers_count,
        'following': following_count
    }


@router.get('/check/{follower_id}/{following_id}')
async def check_if_following(follower_id: int, following_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(followers_table).where(
        (followers_table.c.follower_id == follower_id) &
        (followers_table.c.following_id == following_id)
    )
    result = await session.execute(stmt)
    row = result.fetchone()
    return {'is_following': row is not None}
