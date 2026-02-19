from better_profanity import profanity
from fastapi import HTTPException, APIRouter, UploadFile, File, Depends, Path, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database_files.database import post_table, user_table
from database_files.db_session import get_session
from io import BytesIO
import json
import asyncio
from redis_client import redis_client
from logger import logger
from .rabbit_producer import router as rabbit_router


router = APIRouter(
    tags=['Posts'],
    prefix='/posts'
)


CACHE_NAMESPACE = "posts"
CACHE_TTL = 120


@router.post('/post/create/{author_id}')
async def create_post(
    post_name: str = Form(...),
    text: str = Form(...),
    author_id: int = Path(..., ge=1),
    file: UploadFile = File(None),
    session: AsyncSession = Depends(get_session),
) -> dict:
    picture_data = None

    if profanity.contains_profanity(post_name) or profanity.contains_profanity(text):
        raise HTTPException(status_code=400, detail="Bad words are not allowed")

    if file:
        picture_data = await file.read()

    stmt1 = select(user_table.c.username).where(user_table.c.id == author_id)
    result = await session.execute(stmt1)
    author = result.scalar_one_or_none()

    if author:
        stmt2 = insert(post_table).values(
            post_name=post_name,
            author=author_id,
            text=text,
            picture=picture_data or b"",
            is_approved=1,
        )
        result = await session.execute(stmt2)
        await session.commit()

        inserted_primary_key = result.inserted_primary_key
        new_post_id = inserted_primary_key[0] if inserted_primary_key else None

        if new_post_id is None:
            raise HTTPException(status_code=500, detail="Failed to obtain new post id")

        try:
            await redis_client.delete("fastapi-cache:posts:posts:all")
            logger.info("Cache cleared after post creation")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

        await rabbit_router.broker.publish(
            {
                "post_id": new_post_id,
                "post_name": post_name,
                "text": text
            },
            "ai.moderation.post_create"
        )

        logger.info(f"Background AI check queued for post {new_post_id}")

        return {
            'id': new_post_id,
            'post_name': post_name,
            'author_id': author_id,
            'author_username': author,
            'text': text,
            'picture': picture_data is not None,
        }
    else:
        raise HTTPException(status_code=404, detail='No such author')


@router.get('/post/{post_id}/image')
async def get_post_image(post_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(post_table.c.picture).where(post_table.c.id == post_id)
    result = await session.execute(stmt)
    image = result.scalar_one_or_none()
    
    if image and image != b"":
        return StreamingResponse(BytesIO(image), media_type="image/jpeg")
    raise HTTPException(status_code=404, detail='No image found for this post')


@router.get('/post/get')
async def read_post(post_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(post_table, user_table.c.username).join(
        user_table, post_table.c.author == user_table.c.id
    ).where(post_table.c.id == post_id)
    result = await session.execute(stmt)
    row = result.fetchone()
    
    if row:
        result_dict = {
            'id': row[0],
            'post_name': row[1],
            'author': row[2],
            'author_id': row[2],
            'text': row[3],
            'picture': row[4] is not None,
            'author_username': row[6],
        }
        return result_dict
    raise HTTPException(status_code=404, detail=f'There is no post with id {post_id}')



@router.get("/post/get_all")
async def read_all_posts(
    session: AsyncSession = Depends(get_session),
) -> dict:
    cache_key = "fastapi-cache:posts:posts:all"

    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            logger.debug("Cache hit")
            return json.loads(cached_data)
    except Exception as e:
        logger.error(f"Cache get error: {e}")

    logger.debug("Cache miss, querying database")

    stmt = (
        select(
            post_table.c.id,
            post_table.c.post_name,
            post_table.c.author,
            post_table.c.text,
            post_table.c.picture,
            user_table.c.username,
        )
        .join(user_table, post_table.c.author == user_table.c.id)
        .where(post_table.c.is_approved == 1)
    )

    result = await session.execute(stmt)

    result_dict: dict[int, dict] = {}

    for row in result:
        result_dict[row.id] = {
            "id": row.id,
            "post_name": row.post_name,
            "author_id": row.author,
            "text": row.text,
            "picture": row.picture is not None,
            "author_username": row.username,
        }

    if not result_dict:
        raise HTTPException(status_code=404, detail="There are no posts")

    try:
        await redis_client.set(cache_key, json.dumps(result_dict), ex=CACHE_TTL)
        logger.debug("Result cached")
    except Exception as e:
        logger.error(f"Cache set error: {e}")

    return result_dict



@router.put("/post/update/{post_id}")
async def post_update(
    post_id: int,
    post_name: str = Form(...),
    text: str = Form(...),
    session: AsyncSession = Depends(get_session),
) -> dict:

    stmt_old = (
        select(
            post_table.c.id,
            post_table.c.post_name,
            post_table.c.text,
        )
        .where(post_table.c.id == post_id)
    )
    result_old = await session.execute(stmt_old)
    old_post = result_old.one_or_none()

    if old_post is None:
        raise HTTPException(status_code=404, detail=f"There is no post with id {post_id}")

    old_name = old_post.post_name
    old_text = old_post.text

    stmt_update = (
        update(post_table)
        .where(post_table.c.id == post_id)
        .values(
            post_name=post_name,
            text=text,
            is_approved=1,
        )
    )
    await session.execute(stmt_update)
    await session.commit()

    stmt_get = (
        select(
            post_table.c.id,
            post_table.c.post_name,
            post_table.c.author,
            post_table.c.text,
            post_table.c.picture,
            user_table.c.username,
        )
        .join(user_table, post_table.c.author == user_table.c.id)
        .where(post_table.c.id == post_id)
    )

    result = await session.execute(stmt_get)
    row = result.one()

    post = {
        "id": row.id,
        "post_name": row.post_name,
        "author_id": row.author,
        "text": row.text,
        "picture": row.picture is not None,
        "author_username": row.username,
    }

    try:
        await redis_client.delete("fastapi-cache:posts:posts:all")
    except Exception as e:
        logger.error(f"Cache clear error: {e}")

    await rabbit_router.broker.publish(
        {
            "post_id": post_id,
            "old_name": old_name,
            "old_text": old_text,
            "post_name": post_name,
            "text": text,
        },
        "ai.moderation.post_update"
    )

    return post



@router.delete('/post/delete/{post_id}')
async def post_delete(post_id: int, session: AsyncSession = Depends(get_session)):
    stmt = delete(post_table).where(post_table.c.id == post_id)
    result = await session.execute(stmt)
    await session.commit()
    
    if result.rowcount > 0:
        try:
            await redis_client.delete("fastapi-cache:posts:posts:all")
            logger.info("Cache cleared after post delete")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
        
        return {'message': 'The post has been deleted'}
    else:
        raise HTTPException(status_code=404, detail=f'There is no post with id {post_id}')

@router.get('/post/{user_id}')
async def get_posts_by_user(user_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(post_table, user_table.c.username).join(
        user_table, post_table.c.author == user_table.c.id
    ).where((user_table.c.id == user_id) & (post_table.c.is_approved == 1))
    result = await session.execute(stmt)
    rows = result.fetchall()

    if not rows:
        return {'posts': []}

    posts = []
    for row in rows:
        posts.append({
            'id': row[0],
            'post_name': row[1],
            'author': row[2],
            'author_id': row[2],
            'text': row[3],
            'picture': row[4] is not None,
            'author_username': row[6],
        })

    return {'posts': posts}


@router.get('/post/summary/{post_id}')
async def get_post_summary(post_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(post_table.c.text).where(post_table.c.id == post_id)
    result = await session.execute(stmt)
    post = result.fetchone()

    if not post:
        raise HTTPException(status_code=404, detail=f'Post with id {post_id} not found')

    redis_key = f"summary:{post_id}"

    summary = await redis_client.get(redis_key)
    if summary:
        return {"summary": summary}

    await rabbit_router.broker.publish(
        {
            "text": post.text,
            "post_id": post_id
        },
        "ai.moderation.post_summary"
    )

    for _ in range(9):
        await asyncio.sleep(1)
        summary = await redis_client.get(redis_key)
        if summary:
            return {"summary": summary}

    return {"status": "processing"}





