# Python 3.13 — Per-channel conversation history
# Stores last N exchanges so AI remembers context within a session
import json
import time
from pathlib import Path

CONV_DIR         = Path("data/conversations")
MAX_MESSAGES     = 20    # keep last 20 messages per channel (10 exchanges)
EXPIRE_SECONDS   = 7200  # 2 hours of inactivity = fresh start


def _path(channel_id: str | int) -> Path:
    CONV_DIR.mkdir(parents=True, exist_ok=True)
    return CONV_DIR / f"{channel_id}.json"


def _load(channel_id: str | int) -> list[dict]:
    p = _path(channel_id)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        # expire check
        if data and time.time() - data[-1].get("ts", 0) > EXPIRE_SECONDS:
            p.unlink(missing_ok=True)
            return []
        return data
    except Exception:
        return []


def _save(channel_id: str | int, messages: list[dict]) -> None:
    _path(channel_id).write_text(
        json.dumps(messages[-MAX_MESSAGES:], ensure_ascii=False),
        encoding="utf-8",
    )


def add_message(channel_id: str | int, role: str, content: str) -> None:
    """Append a message to the channel's conversation history."""
    msgs = _load(channel_id)
    msgs.append({"role": role, "content": content[:2000], "ts": time.time()})
    _save(channel_id, msgs)


def get_history(channel_id: str | int) -> list[dict]:
    """Return [{role, content}, ...] ready for OpenRouter messages array."""
    msgs = _load(channel_id)
    return [{"role": m["role"], "content": m["content"]} for m in msgs]


def clear(channel_id: str | int) -> None:
    _path(channel_id).unlink(missing_ok=True)
