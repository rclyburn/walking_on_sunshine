import sys

import structlog
from structlog.stdlib import BoundLogger


def get_logger(name: str) -> BoundLogger:
    return structlog.get_logger(name)


def init_logger():
    """Initialize the logger"""
    if structlog.is_configured():
        print("Logger already initialized")
        return

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.dev.set_exc_info,
        structlog.processors.CallsiteParameterAdder(
            parameters={
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            },
        ),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
    ]

    processors = []
    if sys.stderr.isatty():
        # Pretty printinm when we run in a terminal session.
        # Automatically prints pretty tracebacks when "rich" is installed
        processors = [*shared_processors, structlog.dev.ConsoleRenderer()]
    else:
        # Print JSON when we run, e.g., in a Docker container.
        # Also print structured tracebacks.
        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(processors=processors)
