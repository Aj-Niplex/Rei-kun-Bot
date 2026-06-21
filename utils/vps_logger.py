import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "vps.log"

# BUG FIX #8: renamed logger from "dora_vps" to "rei_vps"
logger = logging.getLogger("rei_vps")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def log_action(action: str, user=None, extra: str = ""):
    user_text = "Unknown User"
    if user:
        user_text = f"{getattr(user, 'name', 'Unknown')} ({getattr(user, 'id', 'N/A')})"

    msg = f"[{action}] by {user_text}"
    if extra:
        msg += f" | {extra}"

    logger.info(msg)


def log_success(action: str, extra: str = ""):
    msg = f"[SUCCESS] {action}"
    if extra:
        msg += f" | {extra}"
    logger.info(msg)


def log_error(action: str, extra: str = ""):
    msg = f"[ERROR] {action}"
    if extra:
        msg += f" | {extra}"
    logger.error(msg)
