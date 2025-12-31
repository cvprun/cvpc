# -*- coding: utf-8 -*-

from argparse import Namespace

from cvpc.aio.run import aio_run
from cvpc.logging.logging import logger


async def _agent_main_async(args: Namespace) -> None:
    from cvpc.apps.agent.handlers import EventHandlerRegistry
    from cvpc.ws import WebSocketClient

    ws_url = args.ws_url
    ws_connect_timeout = args.ws_connect_timeout
    ws_ping_interval = args.ws_ping_interval
    ws_ping_timeout = args.ws_ping_timeout

    if not ws_url:
        logger.error("WebSocket URL is required")
        return

    client = WebSocketClient(
        url=ws_url,
        connect_timeout=ws_connect_timeout,
        ping_interval=ws_ping_interval,
        ping_timeout=ws_ping_timeout,
    )

    # Initialize event handler registry
    event_registry = EventHandlerRegistry()

    async def handle_event(event_type: str, event_data) -> None:
        await event_registry.handle_event(event_type, event_data)

    client.add_event_callback(handle_event)

    try:
        await client.connect()
        logger.info("Agent connected successfully")

        # Keep the agent running
        await client._connected_event.wait()

    except KeyboardInterrupt:
        logger.info("Shutting down agent")
    except Exception as e:
        logger.error(f"Agent error: {e}")
    finally:
        await client.disconnect()
        logger.info("Agent disconnected")


def agent_main(args: Namespace) -> None:
    assert isinstance(args.api_http_bind, str)
    assert isinstance(args.api_http_port, int)
    assert isinstance(args.api_http_timeout, float)
    assert isinstance(args.ws_url, str)
    assert isinstance(args.ws_connect_timeout, float)
    assert isinstance(args.ws_ping_interval, float)
    assert isinstance(args.ws_ping_timeout, float)
    assert isinstance(args.opts, list)

    assert isinstance(args.colored_logging, bool)
    assert isinstance(args.default_logging, bool)
    assert isinstance(args.simple_logging, bool)
    assert isinstance(args.rotate_logging_prefix, str)
    assert isinstance(args.rotate_logging_when, str)

    assert isinstance(args.use_uvloop, bool)
    assert isinstance(args.severity, str)
    assert isinstance(args.debug, bool)
    assert isinstance(args.verbose, int)
    assert isinstance(args.D, bool)

    use_uvloop = args.use_uvloop
    aio_run(_agent_main_async(args), use_uvloop=use_uvloop)
