from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from posts.crud_posts import router as post_router
from twitter_parse.parse_tweet import router as twitter_router
from users.crud_users import router as user_router
from users.oauth import oauth
from comments.crud_comments import router as comment_router
from likes.crud_likes import router as likes_router
from followers.crud_followers import router as followers_router
from chat.crud_chat import router as chat_router
from chat.con_manager import manager as chat_manager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from database_files.database import init_db
from redis_client import redis_client, start_chat_pubsub, stop_chat_pubsub
from posts.rabbit_producer import router as rabbit_router
import posts.rabbit_consumer
from logger import logger as LOGGER
import os
from dotenv import load_dotenv



load_dotenv()

app = FastAPI()
broker = rabbit_router.broker

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("JWT_SECRET_KEY"))


@app.on_event("startup")
async def startup():
    try:
        await init_db()
        await redis_client.ping()
        await broker.start()
        await start_chat_pubsub(chat_manager)
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
        print("Redis cache and RabbitMQ initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Redis cache or RabbitMQ: {e}")


@app.on_event("shutdown")
async def shutdown():
    try:
        await redis_client.close()
        await broker.close()
        await stop_chat_pubsub()
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
app.include_router(chat_router)

# для зручного auth у swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    security_schemes = openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    security_schemes["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "security" in operation:
                operation["security"].append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
