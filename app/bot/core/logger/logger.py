from pathlib import Path

from loguru import logger


BASE_DIR = Path(__file__).resolve().parent.parent


logger.add(
    "logs/bot.log",
    format="{time} {level} {message}",
    level="ERROR",
    rotation="2 MB",
    compression="zip",
    serialize=False
)