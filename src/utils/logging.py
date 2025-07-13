from loguru import logger
from pathlib import Path
import sys

def setup_logger(log_path: Path = Path("logs/app.log")):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(log_path, rotation="1 MB", backtrace=True, diagnose=True, level="INFO")
    logger.add(sys.stderr, level="INFO", format="{time} | {level} | {message}")
    return logger
