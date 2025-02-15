import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name="ai_orchestrator", log_level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    os.makedirs("logs", exist_ok=True)

    file_handler = RotatingFileHandler(
        "logs/orchestrator.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
