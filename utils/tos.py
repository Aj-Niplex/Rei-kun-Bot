"""
Terms of Service tracker.
Tracks which users agreed, and blocks repeat violators.
"""
import json
from pathlib import Path
from utils.storage import block_user

TOS_FILE = Path("data/tos.json")
MAX_ATTEMPTS = 3

TOS_TEXT = """
**📜 Rei-kun — Terms of Use**

By using this bot you agree to:
> • Not abuse, spam, or exploit bot features
> • Not use the bot to harass or harm others
> • Accept that misuse may result in a permanent block
> • Follow Discord's Terms of Service at all times

React **👍** to agree and continue.
React **👎** to decline (you won't be able to use the bot).
""".strip()


def _load() -> dict:
    if not TOS_FILE.exists():
        return {"agreed": [], "attempts": {}}
    try:
        return json.loads(TOS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"agreed": [], "attempts": {}}


def _save(data: dict) -> None:
    TOS_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def has_agreed(user_id: str) -> bool:
    return user_id in _load().get("agreed", [])


def mark_agreed(user_id: str) -> None:
    data = _load()
    if user_id not in data["agreed"]:
        data["agreed"].append(user_id)
    data.setdefault("attempts", {}).pop(user_id, None)
    _save(data)


def increment_attempts(user_id: str) -> int:
    data = _load()
    data.setdefault("attempts", {})
    data["attempts"][user_id] = data["attempts"].get(user_id, 0) + 1
    _save(data)
    return data["attempts"][user_id]


def get_attempts(user_id: str) -> int:
    return _load().get("attempts", {}).get(user_id, 0)


def reset(user_id: str) -> None:
    data = _load()
    data.get("agreed", []).discard if isinstance(data["agreed"], set) else None
    if user_id in data.get("agreed", []):
        data["agreed"].remove(user_id)
    data.get("attempts", {}).pop(user_id, None)
    _save(data)
