# -*- coding: utf-8 -*-

from argparse import Namespace

from cvpc.logging.logging import logger


def cli_main(args: Namespace) -> None:
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

    logger.info("Starting interactive CLI interface")

    # TODO: Implement interactive CLI using prompt_toolkit or similar
    logger.info("Interactive CLI implementation pending")

    try:
        while True:
            try:
                user_input = input("cvpc> ")
                if user_input.lower() in ("exit", "quit", "q"):
                    break
                logger.info(f"Command: {user_input}")
                # TODO: Parse and execute commands
            except EOFError:
                break
    except KeyboardInterrupt:
        logger.info("CLI interrupted")
    finally:
        logger.info("CLI session ended")
