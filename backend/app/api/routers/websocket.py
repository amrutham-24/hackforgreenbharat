import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.auth import ws_get_current_user
from app.db.redis import redis_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, tenant_id: str, websocket: WebSocket):
        await websocket.accept()
        if tenant_id not in self.active:
            self.active[tenant_id] = []
        self.active[tenant_id].append(websocket)

    def disconnect(self, tenant_id: str, websocket: WebSocket):
        if tenant_id in self.active:
            self.active[tenant_id] = [ws for ws in self.active[tenant_id] if ws != websocket]

    async def broadcast(self, tenant_id: str, message: dict):
        if tenant_id in self.active:
            dead = []
            for ws in self.active[tenant_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.active[tenant_id].remove(ws)


manager = ConnectionManager()


@router.websocket("/v1/ws/live")
async def websocket_live(websocket: WebSocket):
    try:
        user = await ws_get_current_user(websocket)
    except Exception:
        return

    await manager.connect(user.tenant_id, websocket)

    async def redis_listener():
        try:
            pubsub = redis_client.pubsub()
            await pubsub.subscribe("esg:live")
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    if data.get("tenant_id") == user.tenant_id:
                        await manager.broadcast(user.tenant_id, data)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Redis listener error: {e}")

    listener_task = asyncio.create_task(redis_listener())

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        listener_task.cancel()
        manager.disconnect(user.tenant_id, websocket)
