from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from posts.crud_posts import router as post_router
from twitter_parse.parse_tweet import router as twitter_router
from users.crud_users import router as user_router
from comments.crud_comments import router as comment_router
from likes.crud_likes import router as likes_router
from followers.crud_followers import router as followers_router
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as redis
from database_files.database import init_db
from redis_client import redis_client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    try:
        await init_db()
        await redis_client.ping()
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
        print("Redis cache initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Redis cache: {e}")


@app.on_event("shutdown")
async def shutdown():
    try:
        await redis_client.close()
        print("Redis cache closed successfully")
    except Exception as e:
        print(f"Failed to close Redis cache: {e}")

app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(twitter_router)
app.include_router(likes_router)
app.include_router(followers_router)
