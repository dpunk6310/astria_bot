from pathlib import Path

from loguru import logger as l




def get_logger():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    log_path = BASE_DIR / "media" / "logs" / "bot.log"
    l.add(
        log_path,
        format="{time} {level} {message}",
        level="ERROR",
        rotation="2 MB",
        compression="zip",
        serialize=False
    )
    return l