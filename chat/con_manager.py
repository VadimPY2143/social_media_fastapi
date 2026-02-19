from fastapi import WebSocket
import asyncio
import json


class ConnectionManager:
    def __init__(self):
        self._connections: dict[int, set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        sockets = self._connections.get(user_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            self._connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, payload: dict):
        sockets = self._connections.get(user_id, set())
        if not sockets:
            return
        message = json.dumps(payload)
        await asyncio.gather(*(ws.send_text(message) for ws in list(sockets)), return_exceptions=True)

    def has_user(self, user_id: int) -> bool:
        return user_id in self._connections


manager = ConnectionManager()