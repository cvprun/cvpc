# -*- coding: utf-8 -*-

import asyncio
from asyncio import Event, Queue, Task, create_task, sleep
from typing import Any, Awaitable, Callable, Optional
from weakref import WeakSet

import msgpack
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from cvpc.logging.logging import logger

EventCallbackType = Callable[[str, Any], Awaitable[None]]


class WebSocketClient:
    """WebSocket client for Cloudflare Durable Objects with hibernation API support"""

    def __init__(
        self,
        url: str,
        connect_timeout: float = 10.0,
        ping_interval: float = 30.0,
        ping_timeout: float = 10.0,
    ) -> None:
        self._url = url
        self._connect_timeout = connect_timeout
        self._ping_interval = ping_interval
        self._ping_timeout = ping_timeout

        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._receive_task: Optional[Task[None]] = None
        self._send_queue: Queue[bytes] = Queue()
        self._send_task: Optional[Task[None]] = None
        self._connected_event = Event()
        self._should_stop = Event()

        self._event_callbacks: WeakSet[EventCallbackType] = WeakSet()

    @property
    def connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self._websocket is not None and not self._websocket.closed

    def add_event_callback(self, callback: EventCallbackType) -> None:
        """Add event callback for incoming messages"""
        self._event_callbacks.add(callback)

    def remove_event_callback(self, callback: EventCallbackType) -> None:
        """Remove event callback"""
        self._event_callbacks.discard(callback)

    async def connect(self) -> None:
        """Connect to WebSocket server"""
        if self.connected:
            logger.warning("WebSocket is already connected")
            return

        try:
            logger.info(f"Connecting to WebSocket: {self._url}")
            self._websocket = await websockets.connect(
                self._url,
                ping_interval=self._ping_interval,
                ping_timeout=self._ping_timeout,
                open_timeout=self._connect_timeout,
            )
            logger.info("WebSocket connected successfully")

            self._connected_event.set()
            self._should_stop.clear()

            # Start background tasks
            self._receive_task = create_task(self._receive_loop())
            self._send_task = create_task(self._send_loop())

        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            await self._cleanup()
            raise

    async def disconnect(self) -> None:
        """Disconnect from WebSocket server"""
        if not self.connected:
            logger.warning("WebSocket is not connected")
            return

        logger.info("Disconnecting from WebSocket")
        self._should_stop.set()
        await self._cleanup()
        logger.info("WebSocket disconnected")

    async def _cleanup(self) -> None:
        """Clean up resources"""
        self._connected_event.clear()

        # Cancel tasks
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except Exception:
                pass
            self._receive_task = None

        if self._send_task and not self._send_task.done():
            self._send_task.cancel()
            try:
                await self._send_task
            except Exception:
                pass
            self._send_task = None

        # Close WebSocket
        if self._websocket:
            try:
                await self._websocket.close()
            except Exception:
                pass
            self._websocket = None

        # Clear send queue
        while not self._send_queue.empty():
            try:
                self._send_queue.get_nowait()
                self._send_queue.task_done()
            except Exception:
                break

    async def _receive_loop(self) -> None:
        """Background task to receive messages"""
        while not self._should_stop.is_set() and self.connected:
            try:
                if self._websocket is None:
                    break

                message = await self._websocket.recv()
                if isinstance(message, bytes):
                    await self._handle_binary_message(message)
                else:
                    logger.warning(f"Received non-binary message: {type(message)}")

            except ConnectionClosed:
                logger.info("WebSocket connection closed")
                break
            except WebSocketException as e:
                logger.error(f"WebSocket error: {e}")
                break
            except Exception as e:
                logger.exception(f"Unexpected error in receive loop: {e}")
                break

        await self._cleanup()

    async def _handle_binary_message(self, data: bytes) -> None:
        """Handle incoming binary message"""
        try:
            message = msgpack.unpackb(data, raw=False)
            if isinstance(message, dict):
                event_type = message.get("type", "unknown")
                event_data = message.get("data", {})
                logger.debug(f"Received event: {event_type}")
                await self._dispatch_event(event_type, event_data)
            else:
                logger.warning(f"Invalid message format: {type(message)}")
        except Exception as e:
            logger.error(f"Failed to handle binary message: {e}")

    async def _dispatch_event(self, event_type: str, event_data: Any) -> None:
        """Dispatch event to all registered callbacks"""
        for callback in list(self._event_callbacks):
            try:
                await callback(event_type, event_data)
            except Exception as e:
                logger.exception(f"Error in event callback for {event_type}: {e}")

    async def _send_loop(self) -> None:
        """Background task to send messages"""
        while not self._should_stop.is_set():
            try:
                # Wait for message with timeout
                message = await self._send_queue.get()

                if self._websocket and self.connected:
                    await self._websocket.send(message)
                    logger.debug(f"Sent message: {len(message)} bytes")
                else:
                    logger.warning("Cannot send message: WebSocket not connected")

                self._send_queue.task_done()

            except Exception as e:
                logger.error(f"Error in send loop: {e}")
                await sleep(0.1)  # Brief pause before retry

    async def send_event(
        self,
        event_type: str,
        event_data: Any = None,
    ) -> None:
        """Send event to server"""
        if not self.connected:
            logger.error("Cannot send event: WebSocket not connected")
            return

        try:
            message = {"type": event_type, "data": event_data}
            packed_message = msgpack.packb(message, use_bin_type=True)
            await self._send_queue.put(packed_message)
            logger.debug(f"Queued event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to send event {event_type}: {e}")

    async def wait_connected(self, timeout: Optional[float] = None) -> bool:
        """Wait for connection to be established"""
        try:
            if timeout:
                await asyncio.wait_for(self._connected_event.wait(), timeout)
            else:
                await self._connected_event.wait()
            return True
        except Exception:
            return False
