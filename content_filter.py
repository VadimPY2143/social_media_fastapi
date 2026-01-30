from openai import OpenAI
import os
from dotenv import load_dotenv
from sqlalchemy import update
from database_files.database import post_table, engine
from sqlalchemy.ext.asyncio import AsyncSession as SQLAsyncSession
from redis import asyncio as redis
import traceback


load_dotenv()

SYSTEM_PROMPT_FILTER = "You are a content filter. Your task is to determine if the given text contains inappropriate content (bad words, hate speech, violence, etc.) Be very careful. Look carefully for any signs of hate speech, violence, or other inappropriate content. Answer with 'Yes' or 'No' only."
SYSTEM_PROMPT_SUMMARY = "You are a content summarizer. Your task is to summarize the given text in a concise and clear manner. You can use up to 250 characters. Answer with a summary of the text in the same language as the story was."


client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def filter_content(post_text: str, post_name: str) -> bool:
    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_FILTER},
                {"role": "user", "content": f"Title: {post_name}\nContent: {post_text}"}
            ],
        )
        result = response.choices[0].message.content.strip().lower()
        is_inappropriate = result == "yes"
        print(f"AI Filter result: {'FLAGGED' if is_inappropriate else 'APPROVED'} - Response: {result}")
        return is_inappropriate
    except Exception as e:
        print(f"AI Filter error: {e}")
        return False

async def check_post_update_async(post_id: int, post_name: str, post_text: str, old_name: str, old_text: str):
    """Background task to check updated post content with rollback support."""
    print(f"Starting AI check for updated post {post_id}...")
    
    is_inappropriate = filter_content(post_text, post_name)
    
    # Update post with approval status or rollback
    try:
        from database_files.database import post_table, engine
        from sqlalchemy.ext.asyncio import AsyncSession as SQLAsyncSession
        
        async with SQLAsyncSession(bind=engine) as session:
            if is_inappropriate:
                # Rollback to old values
                print(f"Rolling back post {post_id} to: name='{old_name}', text='{old_text}'")
                rollback_stmt = update(post_table).where(post_table.c.id == post_id).values(
                    post_name=old_name,
                    text=old_text,
                    is_approved=1
                )
                print(f"Executing rollback statement...")
                result = await session.execute(rollback_stmt)
                print(f"Rollback executed, committing...")
                await session.commit()
                print(f"✓ Post {post_id} FLAGGED - rolled back to previous version (rows updated: {result.rowcount})")
            else:
                stmt = update(post_table).where(post_table.c.id == post_id).values(
                    is_approved=1
                )
                result = await session.execute(stmt)
                await session.commit()
                print(f"✓ Post {post_id} APPROVED by AI filter (rows updated: {result.rowcount})")
        
        try:
            redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=False)
            await redis_client.delete("fastapi-cache:posts:posts:all")
            await redis_client.close()
            print(f"✓ Cache cleared for post {post_id}")
        except Exception as cache_err:
            print(f"Cache clear error: {cache_err}")
    except Exception as e:
        import traceback
        print(f"✗ Failed to update post {post_id}: {e}")
        print(traceback.format_exc())


async def check_post_async(post_id: int, post_name: str, post_text: str):
    print(f"Starting AI check for post {post_id}...")
    
    is_inappropriate = filter_content(post_text, post_name)
    
    try:
        async with SQLAsyncSession(bind=engine) as session:
            approval_status = 0 if is_inappropriate else 1
            print(f"Updating post {post_id} with is_approved={approval_status}")
            
            stmt = update(post_table).where(post_table.c.id == post_id).values(
                is_approved=approval_status
            )
            await session.execute(stmt)
            await session.commit()

            try:
                redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=False)
                await redis_client.delete("fastapi-cache:posts:posts:all")
                await redis_client.close()
                print(f"✓ Cache cleared for post {post_id}")
            except Exception as cache_err:
                print(f"Cache clear error: {cache_err}")
    except Exception as e:
        print(f"✗ Failed to update post {post_id}: {e}")
        print(traceback.format_exc())


async def summarize_content_async(post_text: str):
    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_SUMMARY},
                {"role": "user", "content": f"Content: {post_text}"}
            ],
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        print(f"AI Summary error: {e}")
        return None