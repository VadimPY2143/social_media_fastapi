from fastapi import APIRouter, WebSocket, Depends, Path, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect
from database_files.database import chat_table, message_table, user_table, chat_members_table
from database_files.db_session import get_session
from logger import logger
from users.auth import get_current_user
from redis_client import redis_client
from io import BytesIO
from datetime import datetime
import asyncio
import base64
import json
from .con_manager import manager

router = APIRouter(
    tags=['Chat'],
    prefix='/chat'
)




@router.post('/chat/create/{other_user_id}')
async def create_chat(
    other_user_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user['id'] == other_user_id:
        raise HTTPException(status_code=400, detail="Cannot create chat with yourself")

    stmt_user = select(user_table.c.id).where(user_table.c.id == other_user_id)
    other_user = await session.execute(stmt_user)
    if not other_user.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")

    stmt = (
        select(chat_members_table.c.chat_id)
        .where(chat_members_table.c.user_id.in_([current_user['id'], other_user_id]))
        .group_by(chat_members_table.c.chat_id)
        .having(func.count(func.distinct(chat_members_table.c.user_id)) == 2)
    )
    existing = await session.execute(stmt)
    chat_id = existing.scalar_one_or_none()

    if chat_id:
        return {"chat_id": chat_id}

    result = await session.execute(
        insert(chat_table).values(user_id=current_user['id'])
    )
    await session.commit()
    chat_id = result.inserted_primary_key[0]

    await session.execute(
        insert(chat_members_table).values([
            {"chat_id": chat_id, "user_id": current_user['id']},
            {"chat_id": chat_id, "user_id": other_user_id},
        ])
    )
    await session.commit()

    return {"chat_id": chat_id}


@router.get('/chat/{chat_id}/messages')
async def get_messages(
    chat_id: int = Path(..., ge=1),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict:
    stmt = (
        select(message_table)
        .where(message_table.c.chat_id == chat_id)
        .order_by(message_table.c.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = result.fetchall()
    messages = [
        {
            "id": row.id,
            "chat_id": row.chat_id,
            "user_id": row.user_id,
            "message": row.message,
            "has_image": bool(row.image),
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
    return {"messages": messages}


@router.get('/message/{message_id}/image')
async def get_message_image(
    message_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(message_table.c.image).where(message_table.c.id == message_id)
    result = await session.execute(stmt)
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="No image found for this message")

    content_type = "application/octet-stream"
    if image.startswith(b"\x89PNG\r\n\x1a\n"):
        content_type = "image/png"
    elif image.startswith(b"\xff\xd8"):
        content_type = "image/jpeg"
    elif image.startswith(b"GIF87a") or image.startswith(b"GIF89a"):
        content_type = "image/gif"

    return StreamingResponse(BytesIO(image), media_type=content_type)


@router.websocket('/ws/{chat_id}')
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_session),
):
    token = websocket.query_params.get("token") or websocket.headers.get("authorization")
    if not token:
        await websocket.close(code=1008)
        return

    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()

    try:
        user = await get_current_user(token, session)
    except HTTPException:
        await websocket.close(code=1008)
        return

    stmt_check_chat = select(chat_table).where(chat_table.c.id == chat_id)
    chat_exists = await session.execute(stmt_check_chat)
    if not chat_exists.scalar_one_or_none():
        await websocket.close(code=1008)
        return

    stmt_member = select(chat_members_table).where(
        (chat_members_table.c.chat_id == chat_id) &
        (chat_members_table.c.user_id == user['id'])
    )
    member = await session.execute(stmt_member)
    if not member.scalar_one_or_none():
        await websocket.close(code=1008)
        return

    members_stmt = select(chat_members_table.c.user_id).where(
        chat_members_table.c.chat_id == chat_id
    )
    members_result = await session.execute(members_stmt)
    member_ids = [row.user_id for row in members_result.fetchall()]
    other_member_ids = [uid for uid in member_ids if uid != user['id']]

    await manager.connect(user['id'], websocket)
    logger.info(f"User {user['id']} connected to chat {chat_id}")
    await redis_client.set(f"online:{user['id']}", "1", ex=60)

    for other_id in other_member_ids:
        await redis_client.publish(
            f"user:{other_id}",
            json.dumps({
                "type": "presence",
                "chat_id": chat_id,
                "user_id": user['id'],
                "status": "online",
                "timestamp": datetime.utcnow().isoformat(),
            })
        )

        other_online = await redis_client.exists(f"online:{other_id}")
        await manager.send_to_user(
            user['id'],
            {
                "type": "presence",
                "chat_id": chat_id,
                "user_id": other_id,
                "status": "online" if other_online else "offline",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            if payload.get("type") == "ping":
                await redis_client.set(f"online:{user['id']}", "1", ex=60)
                continue
            to_user_id = int(payload.get("to_user_id"))
            text = (payload.get("text") or "").strip()
            image_b64 = payload.get("image")

            image_bytes = None
            if image_b64:
                try:
                    if isinstance(image_b64, str) and "," in image_b64:
                        image_b64 = image_b64.split(",", 1)[1]
                    image_bytes = base64.b64decode(image_b64)
                except Exception:
                    image_bytes = None

            if not text and not image_bytes:
                continue

            stmt_member_to = select(chat_members_table).where(
                (chat_members_table.c.chat_id == chat_id) &
                (chat_members_table.c.user_id == to_user_id)
            )
            member_to = await session.execute(stmt_member_to)
            if not member_to.scalar_one_or_none():
                continue

            created_at = datetime.utcnow()
            result = await session.execute(
                insert(message_table).values(
                    chat_id=chat_id,
                    user_id=user['id'],
                    message=text,
                    image=image_bytes,
                    created_at=created_at,
                )
            )
            await session.commit()
            message_id = None
            if result.inserted_primary_key:
                message_id = result.inserted_primary_key[0]

            message_payload = {
                "type": "message",
                "id": message_id,
                "chat_id": chat_id,
                "from_user_id": user['id'],
                "to_user_id": to_user_id,
                "text": text,
                "has_image": bool(image_bytes),
                "created_at": created_at.isoformat(),
            }

            await redis_client.publish(f"user:{to_user_id}", json.dumps(message_payload))
            await manager.send_to_user(user['id'], message_payload)
    except WebSocketDisconnect:
        logger.info(f"User {user['id']} disconnected from chat {chat_id}")
    finally:
        await redis_client.delete(f"online:{user['id']}")
        for other_id in other_member_ids:
            await redis_client.publish(
                f"user:{other_id}",
                json.dumps({
                    "type": "presence",
                    "chat_id": chat_id,
                    "user_id": user['id'],
                    "status": "offline",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            )
        manager.disconnect(user['id'], websocket)
