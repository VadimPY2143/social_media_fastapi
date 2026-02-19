from datetime import timedelta
from fastapi import HTTPException, APIRouter, status, Depends, UploadFile, File, Form, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import insert, select, update, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from sqlalchemy import select, insert
import secrets
from database_files.database import user_table
from database_files.db_session import get_session
from users.oauth import oauth
import os
from .models import UpdateUser, UserLogin, Token, UserResponse
from io import BytesIO


from users.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


router = APIRouter(
    tags=['Users'],
    prefix='/users'
)

@router.get('/auth/login/google')
async def login_google(request: Request):
    redirect_uri = "http://localhost:8000/users/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)





@router.get('/auth/callback')
async def google_auth_callback(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Google Auth Error")

    user_info = token.get('userinfo')
    email = user_info.get('email')

    stmt = select(user_table).where(user_table.c.email == email)
    result = await session.execute(stmt)
    db_user = result.fetchone()

    if not db_user:
        random_password = secrets.token_urlsafe(16)
        hashed_password = get_password_hash(random_password)

        stmt = insert(user_table).values(
            username=user_info.get('name') or email.split('@')[0],
            email=email,
            password=hashed_password,
        )
        await session.execute(stmt)
        await session.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )

    frontend_base = os.getenv("FRONTEND", "http://localhost:3000")
    frontend_url = f"{frontend_base}/auth/callback?token={access_token}"
    return RedirectResponse(url=frontend_url)


@router.post('/user/create', response_model=UserResponse)
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    avatar: UploadFile = File(None),
    session: AsyncSession = Depends(get_session)
):
    avatar_data = None
    stmt = select(user_table).where(user_table.c.email == email)
    result = await session.execute(stmt)
    existing_user = result.fetchone()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if avatar:
        avatar_data = await avatar.read()

    hashed_password = get_password_hash(password)
    stmt = insert(user_table).values(
        username=username,
        email=email,
        password=hashed_password,
        avatar=avatar_data
    )

    result = await session.execute(stmt)
    await session.commit()

    user_id = result.lastrowid

    return UserResponse(
        id=user_id,
        username=username,
        email=email,
        password=len(password)*'*',
    )


@router.post('/user/login', response_model=Token)
async def login_user(user: UserLogin, session: AsyncSession = Depends(get_session)):
    stmt = select(user_table).where(user_table.c.email == user.email)
    result = await session.execute(stmt)
    db_user = result.fetchone()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(user.password.get_secret_value(), db_user[3]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get('/user/me', response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(user_table.c.avatar).where(user_table.c.id == current_user['id'])
    result = await session.execute(stmt)
    avatar = result.scalar_one_or_none()
    return UserResponse(**current_user, user_avatar=bool(avatar))


@router.get('/user/search')
async def search_users(
    query: str = Query('', max_length=50),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    stmt = select(user_table.c.id, user_table.c.username, user_table.c.email)
    if query:
        q = f"%{query.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(user_table.c.username).like(q),
                func.lower(user_table.c.email).like(q),
            )
        )
    stmt = stmt.where(user_table.c.id != current_user['id'])
    stmt = stmt.order_by(user_table.c.username.asc()).limit(limit)
    result = await session.execute(stmt)
    users = [
        {"id": row.id, "username": row.username, "email": row.email}
        for row in result.fetchall()
    ]
    return {"users": users}


@router.get('/user/{user_id}', response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(user_table).where(user_table.c.id == user_id)
    result = await session.execute(stmt)
    db_user = result.fetchone()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'There is no user with id {user_id}'
        )
    
    return UserResponse(
        id=db_user[0],
        username=db_user[1],
        email=db_user[2],
        password=len(db_user[3]) * '*',
        user_avatar=bool(db_user[4]) if len(db_user) > 4 else False
    )




@router.put('/user/update', response_model=UserResponse)
async def update_user(
    user_upd: UpdateUser = Depends(),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    user_id = current_user['id']
    
    stmt = select(user_table).where(user_table.c.id == user_id)
    result = await session.execute(stmt)
    user_data = result.fetchone()
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    if not verify_password(user_upd.old_password.get_secret_value(), user_data[3]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Wrong password!'
        )
    
    new_password_hash = None
    if user_upd.new_password:
        new_password_hash = get_password_hash(user_upd.new_password.get_secret_value())
    
    stmt = update(user_table).where(user_table.c.id == user_id).values(
        username=user_upd.new_username if user_upd.new_username else user_data[1],
        email=user_upd.new_email if user_upd.new_email else user_data[2],
        password=new_password_hash if new_password_hash else user_data[3]
    )
    await session.execute(stmt)
    await session.commit()
    
    stmt = select(user_table).where(user_table.c.id == user_id)
    result = await session.execute(stmt)
    updated_user = result.fetchone()
    
    return UserResponse(
        id=updated_user[0],
        username=updated_user[1],
        email=updated_user[2],
        password=len(updated_user[3])*'*'
    )


@router.delete('/user/delete')
async def delete_user(current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> dict:
    user_id = current_user['id']
    
    delete_stmt = delete(user_table).where(user_table.c.id == user_id)
    await session.execute(delete_stmt)
    await session.commit()
    
    return {'message': 'User successfully deleted'}


@router.get('/user/{user_id}/avatar')
async def get_user_avatar(user_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(user_table.c.avatar).where(user_table.c.id == user_id)
    result = await session.execute(stmt)
    avatar = result.scalar_one_or_none()
    
    if avatar and avatar != b"":
        return StreamingResponse(BytesIO(avatar), media_type="image/jpeg")
    
    raise HTTPException(status_code=404, detail='No avatar found for this user')


@router.put('/user/avatar')
async def update_user_avatar(
    avatar: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    user_id = current_user['id']
    
    if not avatar:
        raise HTTPException(status_code=400, detail='Avatar file is required')
    
    try:
        avatar_data = await avatar.read()
        
        stmt = update(user_table).where(user_table.c.id == user_id).values(
            avatar=avatar_data
        )
        await session.execute(stmt)
        await session.commit()
        
        return {'message': 'Avatar updated successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to upload avatar: {str(e)}')


@router.delete('/user/avatar')
async def delete_user_avatar(current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> dict:
    user_id = current_user['id']

    stmt = update(user_table).where(user_table.c.id == user_id).values(
        avatar=None
    )
    await session.execute(stmt)
    await session.commit()

    return {'message': 'Avatar deleted successfully'}
