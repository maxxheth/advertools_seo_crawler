"""
WebSocket Server - Real-time crawl monitoring
"""
import asyncio
import json
from datetime import datetime
from typing import Set, Dict, Any
from pathlib import Path


class WebSocketManager:
    """
    Manages WebSocket connections for real-time crawl monitoring.
    Broadcasts crawl progress events to connected clients.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        """
        Initialize WebSocket manager.

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.connected_clients: Set = set()
        self.server = None

    async def start(self):
        """Start the WebSocket server."""
        try:
            import websockets
        except ImportError:
            raise ImportError("websockets is required. Install with: pip install websockets")

        async def handler(websocket, path):
            self.connected_clients.add(websocket)
            try:
                async for message in websocket:
                    # Echo or process incoming messages if needed
                    pass
            finally:
                self.connected_clients.remove(websocket)

        self.server = await websockets.serve(handler, self.host, self.port)
        print(f"WebSocket server started on ws://{self.host}:{self.port}")

    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
        """
        if not self.connected_clients:
            return

        message_json = json.dumps(message, default=str)

        # Send to all connected clients
        disconnected = set()
        for client in self.connected_clients:
            try:
                await client.send(message_json)
            except Exception as e:
                print(f"Error sending message to client: {e}")
                disconnected.add(client)

        # Remove disconnected clients
        self.connected_clients -= disconnected

    async def send_crawl_start(self, crawler_type: str, start_urls: list):
        """Send crawl start event."""
        await self.broadcast({
            "event": "crawl_start",
            "crawler": crawler_type,
            "start_urls": start_urls,
            "timestamp": datetime.now().isoformat(),
        })

    async def send_page_crawled(self, crawler_type: str, url: str, page_count: int):
        """Send page crawled event."""
        await self.broadcast({
            "event": "page_crawled",
            "crawler": crawler_type,
            "url": url,
            "page_count": page_count,
            "timestamp": datetime.now().isoformat(),
        })

    async def send_crawl_complete(self, crawler_type: str, total_pages: int, duration: float):
        """Send crawl complete event."""
        await self.broadcast({
            "event": "crawl_complete",
            "crawler": crawler_type,
            "total_pages": total_pages,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
        })

    async def send_analysis_progress(self, crawler_type: str, progress: int, message: str):
        """Send analysis progress event."""
        await self.broadcast({
            "event": "analysis_progress",
            "crawler": crawler_type,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        })

    async def send_error(self, crawler_type: str, error: str):
        """Send error event."""
        await self.broadcast({
            "event": "error",
            "crawler": crawler_type,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        })

    async def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket server stopped")
