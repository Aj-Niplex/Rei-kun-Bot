"""
Converts :name: and [[key]] patterns into Discord emoji tags.
Reads dynamically from emoji_catalog.json — no hardcoding needed.
"""
import json
import re
from pathlib import Path
from utils.config_loader import EMOJI_CATALOG_FILE


def _build_map() -> dict[str, str]:
    p = Path(EMOJI_CATALOG_FILE)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

    result: dict[str, str] = {}
    seen: set[str] = set()
    for entry in data:
        if not isinstance(entry, dict):
            continue
        emoji_id = str(entry.get("emoji_id", "")).strip()
        name     = str(entry.get("discord_name") or entry.get("key") or "").strip()
        key      = str(entry.get("key") or name).strip().lower()
        animated = bool(entry.get("animated"))
        if not emoji_id or not name or emoji_id in seen:
            continue
        seen.add(emoji_id)
        prefix = "a" if animated else ""
        tag    = f"<{prefix}:{name}:{emoji_id}>" if prefix else f"<:{name}:{emoji_id}>"
        # Register under multiple lookup keys
        result[f":{name}:"]  = tag
        result[f":{key}:"]   = tag
        result[name.lower()] = tag
        result[key]          = tag
    return result


def parse_emojis(text: str) -> str:
    """Replace :name: and [[key]] patterns with real Discord emoji tags."""
    if not text:
        return text
    emoji_map = _build_map()
    if not emoji_map:
        return text

    # :name: patterns
    def _replace_colon(m: re.Match) -> str:
        return emoji_map.get(m.group(0), m.group(0))
    text = re.sub(r":[A-Za-z0-9_]+:", _replace_colon, text)

    # [[key]] patterns
    def _replace_bracket(m: re.Match) -> str:
        k = m.group(1).strip().lower()
        return emoji_map.get(k, m.group(0))
    text = re.sub(r"\[\[([A-Za-z0-9_]+)\]\]", _replace_bracket, text)

    return text


def list_emojis() -> list[dict]:
    p = Path(EMOJI_CATALOG_FILE)
    if not p.exists():
        return []
    try:
        return [e for e in json.loads(p.read_text(encoding="utf-8")) if isinstance(e, dict)]
    except Exception:
        return []
