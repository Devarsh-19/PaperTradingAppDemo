"""
WebSocket order updates endpoint.

Authenticated clients receive push notifications when their orders are filled,
cancelled, or rejected.
"""

import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.core.security import decode_token
from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/orders")
async def order_updates(websocket: WebSocket):
    """
    WebSocket endpoint for user-specific order update notifications.

    Client must send an auth message first:
    {"action": "auth", "token": "<JWT access token>"}

    After auth, the server pushes:
    {"event": "order_filled", "data": {"order_id": "...", ...}}
    {"event": "order_cancelled", "data": {"order_id": "...", ...}}
    {"event": "portfolio_update", "data": {"total_value": ..., ...}}
    """
    connection_id = str(uuid.uuid4())
    user_id = None

    await manager.connect(websocket, connection_id)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                continue

            action = message.get("action")

            if action == "auth":
                token = message.get("token")
                if not token:
                    await websocket.send_text(
                        json.dumps({"error": "Token required"})
                    )
                    continue

                payload = decode_token(token)
                if not payload or payload.get("type") != "access":
                    await websocket.send_text(
                        json.dumps({"error": "Invalid or expired token"})
                    )
                    continue

                user_id = payload["sub"]
                # Re-register with user_id
                manager.disconnect(connection_id)
                await manager.connect(websocket, connection_id, user_id=user_id)

                await websocket.send_text(
                    json.dumps({
                        "event": "authenticated",
                        "data": {"user_id": user_id},
                    })
                )
                logger.info(f"Order updates client authenticated: user={user_id}")

            elif action == "ping":
                await websocket.send_text(
                    json.dumps({"event": "pong"})
                )
            else:
                await websocket.send_text(
                    json.dumps({
                        "error": "Send {\"action\": \"auth\", \"token\": \"...\"} to authenticate",
                    })
                )

    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id=user_id)
        logger.info(f"Order updates client disconnected: {connection_id}")
