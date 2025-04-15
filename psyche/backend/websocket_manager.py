"""WebSocket connection manager for handling canvas connections."""

import asyncio
import logging
import uuid
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from config import CONNECTION_LOG_INTERVAL, CANVAS_SLUGS

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for different canvases."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.connections: Dict[str, Set[WebSocket]] = {
            slug: set() for slug in CANVAS_SLUGS
        }
        self._log_task = None

    async def start(self):
        """Start the connection logging task."""
        self._log_task = asyncio.create_task(self._log_connections())
        logger.info("WebSocket manager started")

    async def stop(self):
        """Stop the connection logging task and close all connections."""
        if self._log_task:
            self._log_task.cancel()
        for canvas_slug, connections in self.connections.items():
            for connection in connections:
                try:
                    await connection.close()
                except Exception as e:
                    logger.error(f"Error closing connection for canvas {canvas_slug}: {str(e)}")
        logger.info("WebSocket manager stopped")

    async def _log_connections(self):
        """Periodically log the number of active connections per canvas."""
        while True:
            for canvas_slug, connections in self.connections.items():
                logger.info(
                    f"Canvas '{canvas_slug}' has {len(connections)} active connections"
                )
            await asyncio.sleep(CONNECTION_LOG_INTERVAL)

    async def connect(self, websocket: WebSocket, canvas_slug: str):
        """Handle a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            canvas_slug: The canvas to connect to
            
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if canvas_slug not in self.connections:
            logger.error(f"Invalid canvas slug: {canvas_slug}")
            return False

        client_id = str(uuid.uuid4())[:8]
        await websocket.accept()
        self.connections[canvas_slug].add(websocket)
        logger.info(
            f"New connection established for canvas '{canvas_slug}' "
            f"(Client ID: {client_id}). Total connections: {len(self.connections[canvas_slug])}"
        )
        return True

    async def disconnect(self, websocket: WebSocket, canvas_slug: str):
        """Handle a WebSocket disconnection.
        
        Args:
            websocket: The WebSocket connection
            canvas_slug: The canvas to disconnect from
        """
        if websocket in self.connections[canvas_slug]:
            self.connections[canvas_slug].remove(websocket)
            logger.info(
                f"Connection closed for canvas '{canvas_slug}'. "
                f"Remaining connections: {len(self.connections[canvas_slug])}"
            )

    def get_connections(self, canvas_slug: str) -> Set[WebSocket]:
        """Get all connections for a specific canvas.
        
        Args:
            canvas_slug: The canvas to get connections for
            
        Returns:
            Set[WebSocket]: Set of active connections
        """
        return self.connections.get(canvas_slug, set()) 