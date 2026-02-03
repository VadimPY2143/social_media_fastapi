from .rabbit_producer import router
from content_filter import check_post_async, check_post_update_async, summarize_content_async
from redis_client import redis_client


@router.subscriber("ai.moderation.post_create")
async def handle_ai_moderation(message: dict):
    await check_post_async(
        post_id=message["post_id"],
        post_name=message["post_name"],
        post_text=message["text"],
    )

@router.subscriber("ai.moderation.post_update")
async def handle_ai_moderation_update(message: dict):
    await check_post_update_async(
        post_id=message["post_id"],
        post_name=message["post_name"],
        post_text=message["text"],
        old_name=message["old_name"],
        old_text=message["old_text"],
    )

@router.subscriber("ai.moderation.post_summary")
async def handle_ai_moderation_summary(message: dict):
    post_id = message["post_id"]
    summary = await summarize_content_async(post_text=message["text"])
    await redis_client.setex(f"summary:{post_id}", 300, summary)  # кеш на 5 хвилин
