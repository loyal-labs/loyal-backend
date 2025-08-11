import logging
import os

import colorlog

LOG_COLORS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}


def configure_logging() -> None:
    console_handler = colorlog.StreamHandler()

    level = os.getenv("LOGGING_LEVEL", "DEBUG").upper()
    level = getattr(logging, level)

    log_format = "%(log_color)s%(levelname)-8s%(reset)s | %(asctime)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"  # noqa: E501
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = colorlog.ColoredFormatter(
        fmt=log_format,
        datefmt=date_format,
        reset=True,
        log_colors=LOG_COLORS,
        secondary_log_colors={},
        style="%",
    )
    console_handler.setFormatter(formatter)

    handlers = [
        console_handler,
    ]

    logging.getLogger("pyrogram").setLevel(logging.INFO)
    logging.getLogger("clickhouse_connect").setLevel(logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(levelname)-8s | %(asctime)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",  # noqa: E501
        datefmt=date_format,
        handlers=handlers,
    )
