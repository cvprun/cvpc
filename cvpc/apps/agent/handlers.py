# -*- coding: utf-8 -*-

from typing import Any, Dict, Protocol

from cvpc.logging.logging import logger


class EventHandler(Protocol):
    """Protocol for event handlers"""

    async def handle(self, event_data: Any) -> None:
        """Handle event data"""
        ...


class PingEventHandler:
    """Handler for ping events"""

    async def handle(self, event_data: Any) -> None:
        logger.debug("Received ping event")


class MessageEventHandler:
    """Handler for message events"""

    async def handle(self, event_data: Any) -> None:
        logger.info(f"Received message: {event_data}")


class TaskEventHandler:
    """Handler for task events"""

    async def handle(self, event_data: Any) -> None:
        logger.info(f"Received task event: {event_data}")
        # TODO: Implement task execution logic


class StatusEventHandler:
    """Handler for status events"""

    async def handle(self, event_data: Any) -> None:
        logger.info(f"Status update: {event_data}")


class DefaultEventHandler:
    """Default handler for unknown events"""

    async def handle(self, event_data: Any) -> None:
        logger.warning(f"Unknown event data: {event_data}")


class EventHandlerRegistry:
    """Registry for event handlers"""

    def __init__(self) -> None:
        self._handlers: Dict[str, EventHandler] = {}
        self._default_handler = DefaultEventHandler()

        # Register default handlers
        self.register("ping", PingEventHandler())
        self.register("message", MessageEventHandler())
        self.register("task", TaskEventHandler())
        self.register("status", StatusEventHandler())

    def register(self, event_type: str, handler: EventHandler) -> None:
        """Register an event handler"""
        self._handlers[event_type] = handler
        logger.debug(f"Registered handler for event type: {event_type}")

    def unregister(self, event_type: str) -> None:
        """Unregister an event handler"""
        if event_type in self._handlers:
            del self._handlers[event_type]
            logger.debug(f"Unregistered handler for event type: {event_type}")

    async def handle_event(self, event_type: str, event_data: Any) -> None:
        """Handle an event using the appropriate handler"""
        handler = self._handlers.get(event_type, self._default_handler)
        try:
            await handler.handle(event_data)
        except Exception as e:
            logger.exception(f"Error handling event {event_type}: {e}")
