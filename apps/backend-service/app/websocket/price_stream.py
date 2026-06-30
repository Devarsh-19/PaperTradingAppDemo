"""
WebSocket price streaming endpoint.

Clients connect, subscribe to symbols, and receive real-time price updates
pushed from the background price_sync task.
"""

import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/prices")
async def price_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time price updates.

    Protocol:
    - Client sends: {"action": "subscribe", "symbols": ["AAPL", "GOOGL"]}
    - Client sends: {"action": "unsubscribe", "symbols": ["AAPL"]}
    - Server pushes: {"event": "price_update", "data": {"symbol": "AAPL", "price": 198.50, ...}}
    """
    connection_id = str(uuid.uuid4())
    await manager.connect(websocket, connection_id)

    try:
        while True:
            # Wait for client messages (subscribe/unsubscribe)
            raw = await websocket.receive_text()

            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps({"error": "Invalid JSON"})
                )
                continue

            action = message.get("action")
            symbols = message.get("symbols", [])

            if action == "subscribe" and symbols:
                manager.subscribe(connection_id, symbols)
                await websocket.send_text(
                    json.dumps({
                        "event": "subscribed",
                        "data": {"symbols": symbols},
                    })
                )
            elif action == "unsubscribe" and symbols:
                manager.unsubscribe(connection_id, symbols)
                await websocket.send_text(
                    json.dumps({
                        "event": "unsubscribed",
                        "data": {"symbols": symbols},
                    })
                )
            else:
                await websocket.send_text(
                    json.dumps({
                        "error": "Unknown action. Use 'subscribe' or 'unsubscribe'.",
                    })
                )

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info(f"Price stream client disconnected: {connection_id}")
