import sys
import logging


def _get_logger() -> logging.Logger:
    formatter = logging.Formatter(
        "%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s"
    )

    logger = logging.getLogger("sticky_controller")
    logger.setLevel(logging.INFO)

    # ensure we don't create a new handler each time the package is reloaded
    if len(logger.handlers) == 0:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


log = _get_logger()
