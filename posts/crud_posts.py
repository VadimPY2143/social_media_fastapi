from better_profanity import profanity
from fastapi import HTTPException, APIRouter, UploadFile, File, Depends, Path, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database_files.database import post_table, user_table
from database_files.db_session import get_session
from io import BytesIO
from content_filter import check_post_async, check_post_update_async, summarize_content_async
import json
from redis import asyncio as redis


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
    background_tasks: BackgroundTasks = BackgroundTasks()
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
            redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=False)
            await redis_client.delete("fastapi-cache:posts:posts:all")
            await redis_client.close()
            print("✓ Cache cleared after post creation")
        except Exception as e:
            print(f"✗ Cache clear error: {e}")

        background_tasks.add_task(check_post_async, new_post_id, post_name, text)
        print(f"✓ Background AI check queued for post {new_post_id}")

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
    redis_client = None
    
    try:
        redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            print("✓ Cache hit")
            await redis_client.close()
            return json.loads(cached_data)
    except Exception as e:
        print(f"Cache get error: {e}")
    finally:
        if redis_client:
            await redis_client.close()

    print("✗ Cache miss, querying database")

    stmt = (
        select(post_table, user_table.c.username)
        .join(user_table, post_table.c.author == user_table.c.id)
        .where(post_table.c.is_approved == 1)
    )
    result = await session.execute(stmt)

    result_dict: dict[int, dict] = {}

    for row in result:
        post = {
            "id": row[0],
            "post_name": row[1],
            "author_id": row[2],
            "text": row[3],
            "picture": row[4] is not None,
            "author_username": row[6],
        }

        result_dict[row[0]] = post

    if not result_dict:
        raise HTTPException(status_code=404, detail="There are no posts")

    try:
        redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        await redis_client.set(cache_key, json.dumps(result_dict), ex=CACHE_TTL)
        print("✓ Result cached")
        await redis_client.close()
    except Exception as e:
        print(f"Cache set error: {e}")

    return result_dict


@router.put('/post/update/{post_id}')
async def post_update(
    post_id: int,
    post_name: str = Form(...),
    text: str = Form(...),
    session: AsyncSession = Depends(get_session),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> dict:

    stmt_get_old = select(post_table).where(post_table.c.id == post_id)
    result_old = await session.execute(stmt_get_old)
    old_post = result_old.fetchone()
    
    if not old_post:
        raise HTTPException(status_code=404, detail=f'There is no post with id {post_id}')
    
    old_name = old_post[1]
    old_text = old_post[3]

    stmt = update(post_table).where(post_table.c.id == post_id).values(
        post_name=post_name, 
        text=text,
        is_approved=1
    )
    await session.execute(stmt)
    await session.commit()

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
        
        try:
            redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=False)
            await redis_client.delete("fastapi-cache:posts:posts:all")
            await redis_client.close()
            print("✓ Cache cleared after post update")
        except Exception as e:
            print(f"✗ Cache clear error: {e}")
        
        background_tasks.add_task(check_post_update_async, post_id, post_name, text, old_name, old_text)
        print(f"✓ Background AI check queued for post {row[0]} (with rollback support)")
        
        return result_dict
    raise HTTPException(status_code=404, detail=f'There is no post with id {post_id}')


@router.delete('/post/delete/{post_id}')
async def post_delete(post_id: int, session: AsyncSession = Depends(get_session)):
    stmt = delete(post_table).where(post_table.c.id == post_id)
    result = await session.execute(stmt)
    await session.commit()
    
    if result.rowcount > 0:
        try:
            redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=False)
            await redis_client.delete("fastapi-cache:posts:posts:all")
            await redis_client.close()
            print("✓ Cache cleared after post delete")
        except Exception as e:
            print(f"✗ Cache clear error: {e}")
        
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
        raise HTTPException(status_code=404, detail=f'No posts found for user with id {user_id}')

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
    stmt = select(post_table).where(post_table.c.id == post_id)
    result = await session.execute(stmt)
    post = result.fetchone()

    if not post:
        raise HTTPException(status_code=404, detail=f'Post with id {post_id} not found')

    summary = await summarize_content_async(post[3])
    if not summary:
        raise HTTPException(status_code=500, detail='Failed to generate summary')

    return {'summary': summary}

