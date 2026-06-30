"""
WebSocket connection manager — handles client connections, subscriptions,
and broadcasting messages to connected clients.
"""

import json
import uuid
from typing import Dict, Set

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """
    Manages WebSocket connections and symbol subscriptions.

    Each client can subscribe to specific stock symbols for price updates
    and receive user-specific order notifications.
    """

    def __init__(self):
        # Active WebSocket connections: connection_id → WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # Symbol subscriptions: symbol → set of connection_ids
        self.symbol_subscriptions: Dict[str, Set[str]] = {}

        # User connections: user_id → set of connection_ids
        self.user_connections: Dict[str, Set[str]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: str | None = None,
    ) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)

        logger.info(f"WebSocket connected: {connection_id} (user={user_id})")

    def disconnect(self, connection_id: str, user_id: str | None = None) -> None:
        """Remove a disconnected WebSocket."""
        self.active_connections.pop(connection_id, None)

        # Remove from all symbol subscriptions
        for symbol_subs in self.symbol_subscriptions.values():
            symbol_subs.discard(connection_id)

        # Remove from user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"WebSocket disconnected: {connection_id}")

    def subscribe(self, connection_id: str, symbols: list[str]) -> None:
        """Subscribe a connection to price updates for specific symbols."""
        for symbol in symbols:
            symbol = symbol.upper().strip()
            if symbol not in self.symbol_subscriptions:
                self.symbol_subscriptions[symbol] = set()
            self.symbol_subscriptions[symbol].add(connection_id)

        logger.debug(f"Connection {connection_id} subscribed to: {symbols}")

    def unsubscribe(self, connection_id: str, symbols: list[str]) -> None:
        """Unsubscribe a connection from specific symbols."""
        for symbol in symbols:
            symbol = symbol.upper().strip()
            if symbol in self.symbol_subscriptions:
                self.symbol_subscriptions[symbol].discard(connection_id)

    async def broadcast_price_update(self, symbol: str, data: dict) -> None:
        """
        Send a price update to all clients subscribed to a symbol.
        """
        symbol = symbol.upper()
        connection_ids = self.symbol_subscriptions.get(symbol, set())

        message = json.dumps({
            "event": "price_update",
            "data": data,
        })

        disconnected = []
        for conn_id in connection_ids:
            ws = self.active_connections.get(conn_id)
            if ws:
                try:
                    await ws.send_text(message)
                except Exception:
                    disconnected.append(conn_id)

        # Clean up broken connections
        for conn_id in disconnected:
            self.disconnect(conn_id)

    async def send_to_user(self, user_id: str, event: str, data: dict) -> None:
        """
        Send a message to all of a specific user's connections.

        Used for order updates, portfolio changes, etc.
        """
        connection_ids = self.user_connections.get(user_id, set())

        message = json.dumps({
            "event": event,
            "data": data,
        })

        disconnected = []
        for conn_id in connection_ids:
            ws = self.active_connections.get(conn_id)
            if ws:
                try:
                    await ws.send_text(message)
                except Exception:
                    disconnected.append(conn_id)

        for conn_id in disconnected:
            self.disconnect(conn_id, user_id)

    async def broadcast_all(self, event: str, data: dict) -> None:
        """Broadcast a message to ALL connected clients."""
        message = json.dumps({"event": event, "data": data})

        disconnected = []
        for conn_id, ws in self.active_connections.items():
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(conn_id)

        for conn_id in disconnected:
            self.disconnect(conn_id)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)

    @property
    def subscribed_symbols(self) -> list[str]:
        """All symbols with at least one subscriber."""
        return [s for s, conns in self.symbol_subscriptions.items() if conns]


# ── Global singleton ──
manager = ConnectionManager()
