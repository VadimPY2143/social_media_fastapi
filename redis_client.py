import asyncio
import json
from typing import Optional
import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.from_url(
    os.getenv("REDIS"),
    decode_responses=True,
)

_chat_pubsub_task: Optional[asyncio.Task] = None


async def _chat_pubsub_listener(manager) -> None:
    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("user:*")
    try:
        async for message in pubsub.listen():
            if message.get("type") != "pmessage":
                continue
            channel = message.get("channel", "")
            data = message.get("data", "")
            if not channel or not data:
                continue
            try:
                user_id = int(channel.split(":")[1])
            except (IndexError, ValueError):
                continue
            if manager.has_user(user_id):
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    continue
                await manager.send_to_user(user_id, payload)
    finally:
        await pubsub.close()


async def start_chat_pubsub(manager) -> None:
    global _chat_pubsub_task
    if _chat_pubsub_task is None or _chat_pubsub_task.done():
        _chat_pubsub_task = asyncio.create_task(_chat_pubsub_listener(manager))


async def stop_chat_pubsub() -> None:
    global _chat_pubsub_task
    if _chat_pubsub_task and not _chat_pubsub_task.done():
        _chat_pubsub_task.cancel()
        _chat_pubsub_task = None
