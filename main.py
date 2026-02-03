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
from posts.rabbit_producer import router as rabbit_router
from posts.rabbit_consumer import handle_ai_moderation
from logger import logger as LOGGER


app = FastAPI()
broker = rabbit_router.broker

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
        await broker.start()
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
        print("Redis cache and RabbitMQ initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Redis cache or RabbitMQ: {e}")


@app.on_event("shutdown")
async def shutdown():
    try:
        await redis_client.close()
        await broker.close()
        LOGGER.info("Redis cache and RabbitMQ closed successfully")
    except Exception as e:
        LOGGER.error(f"Failed to close Redis cache or RabbitMQ: {e}")

app.include_router(rabbit_router)
app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(twitter_router)
app.include_router(likes_router)
app.include_router(followers_router)
