from fastapi import HTTPException, APIRouter
from fastapi.params import Depends
from sqlalchemy import insert, select, delete, func
from sqlalchemy.orm import Session
from database import followers_table, user_table, engine
from followers.models import Follow


router = APIRouter(
    tags=['Followers'],
    prefix='/followers'
)


@router.post('/follow')
def follow_user(follow: Follow = Depends()) -> dict:
    with Session(engine) as session:
        if follow.follower_id == follow.following_id:
            raise HTTPException(status_code=400, detail='You cannot follow yourself')
        
        stmt_check_user = select(user_table).where(user_table.c.id == follow.following_id)
        user_exists = session.execute(stmt_check_user).fetchone()
        
        if not user_exists:
            raise HTTPException(status_code=404, detail=f'User with id {follow.following_id} not found')
        
        stmt_check_follow = select(followers_table).where(
            (followers_table.c.follower_id == follow.follower_id) &
            (followers_table.c.following_id == follow.following_id)
        )
        existing_follow = session.execute(stmt_check_follow).fetchone()
        
        if existing_follow:
            raise HTTPException(status_code=400, detail='You already follow this user')
        
        stmt = insert(followers_table).values(
            follower_id=follow.follower_id,
            following_id=follow.following_id
        )
        session.execute(stmt)
        session.commit()

        username = user_exists[1]
        return {'message': f'You are now following {username}'}


@router.delete('/unfollow')
def unfollow_user(follower_id: int, following_id: int) -> dict:
    with Session(engine) as session:
        stmt = delete(followers_table).where(
            (followers_table.c.follower_id == follower_id) & 
            (followers_table.c.following_id == following_id)
        )
        result = session.execute(stmt)
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail='Follow relationship not found')
        
        session.commit()
        return {'message': f'You unfollowed user {following_id}'}


@router.get('/followers/{user_id}')
def get_followers(user_id: int) -> dict:
    with Session(engine) as session:
        stmt = select(
            followers_table.c.follower_id,
            user_table.c.username).join(
            user_table,
            user_table.c.id == followers_table.c.follower_id).where(
            followers_table.c.following_id == user_id)
        
        result = session.execute(stmt).fetchall()
        followers = []
        for follower in result:
            fol_info = {'id': follower[0],
                        'username': follower[1]}
            followers.append(fol_info)
        
        return {
            'user_id': user_id,
            'followers_count': len(followers),
            'followers': followers
        }


@router.get('/following/{user_id}')
def get_following(user_id: int) -> dict:
    with Session(engine) as session:
        stmt = select(
            followers_table.c.following_id,
            user_table.c.username
        ).join(
            user_table,
            user_table.c.id == followers_table.c.following_id
        ).where(
            followers_table.c.follower_id == user_id
        )
        
        result = session.execute(stmt).fetchall()
        
        following_list = [
            {'user_id': row[0], 'username': row[1]} 
            for row in result
        ]
        
        return {
            'user_id': user_id,
            'following_count': len(following_list),
            'following': following_list
        }


@router.get('/stats/{user_id}')
def get_follower_stats(user_id: int) -> dict:
    with Session(engine) as session:
        followers_stmt = select(func.count()).select_from(followers_table).where(
            followers_table.c.following_id == user_id
        )
        followers_count = session.execute(followers_stmt).scalar()
        
        following_stmt = select(func.count()).select_from(followers_table).where(
            followers_table.c.follower_id == user_id
        )
        following_count = session.execute(following_stmt).scalar()
        
        return {
            'user_id': user_id,
            'followers': followers_count,
            'following': following_count
        }
