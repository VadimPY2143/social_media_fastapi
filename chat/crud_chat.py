from fastapi import APIRouter, WebSocket, Depends, Path, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect
from database_files.database import chat_table
from database_files.db_session import get_session

router = APIRouter(
    tags=['Chat'],
    prefix='/chat'
)

@router.websocket('/chat/{chat_id}/')
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session), chat_id: int = Path(..., ge=1)):
    await websocket.accept()
    stmt_check_chat = select(chat_table).where(chat_table.c.id == chat_id)
    chat_exists = await session.execute(stmt_check_chat)
    if not chat_exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f'Chat with id {chat_id} not found')
    try:
        while True:
            data = await websocket.receive_text()
            
    except WebSocketDisconnect:
        print("WebSocket connection closed")
