# -*- coding: utf-8 -*-

import asyncio
from argparse import Namespace

from cvpc.aio.run import aio_run
from cvpc.logging.logging import logger


async def _server_main_async(args: Namespace) -> None:
    """Async main function for HTTP API server"""
    api_http_bind = args.api_http_bind
    api_http_port = args.api_http_port
    api_http_timeout = args.api_http_timeout

    logger.info(f"Starting HTTP API server on {api_http_bind}:{api_http_port}")
    logger.info(f"Timeout: {api_http_timeout}s")

    # TODO: Implement HTTP API server using FastAPI or similar
    logger.info("HTTP API server implementation pending")

    try:
        # Keep server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down HTTP API server")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("HTTP API server stopped")


def server_main(args: Namespace) -> None:
    assert isinstance(args.api_http_bind, str)
    assert isinstance(args.api_http_port, int)
    assert isinstance(args.api_http_timeout, float)
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
    aio_run(_server_main_async(args), use_uvloop=use_uvloop)
