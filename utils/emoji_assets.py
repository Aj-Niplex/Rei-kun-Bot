"""
Provides emoji/asset context for AI prompts and renders [[key]] placeholders.
"""
import json
import re
from pathlib import Path
from utils.config_loader import EMOJI_CATALOG_FILE


def _load_catalog() -> list[dict]:
    p = Path(EMOJI_CATALOG_FILE)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return [e for e in data if isinstance(e, dict)]
    except Exception:
        return []


def build_emoji_context(max_items: int = 80) -> str:
    """
    Build a text block for AI system prompt listing available emojis.
    Format: [[key]] → <:name:id>
    """
    catalog = _load_catalog()
    if not catalog:
        return ""
    lines = []
    seen = set()
    for entry in catalog[:max_items]:
        emoji_id = str(entry.get("emoji_id", "")).strip()
        name     = str(entry.get("discord_name") or entry.get("key") or "").strip()
        key      = str(entry.get("key") or name).strip().lower()
        animated = entry.get("animated", False)
        if not emoji_id or not name or emoji_id in seen:
            continue
        seen.add(emoji_id)
        prefix = "a" if animated else ""
        tag    = f"<{prefix}:{name}:{emoji_id}>" if prefix else f"<:{name}:{emoji_id}>"
        lines.append(f"[[{key}]] → {tag}")
    return "\n".join(lines)


def render_asset_placeholders(text: str) -> str:
    """Replace [[key]] placeholders with Discord emoji tags."""
    if not text:
        return text
    catalog = _load_catalog()
    if not catalog:
        return text

    # Build lookup: key → tag
    lookup: dict[str, str] = {}
    for entry in catalog:
        emoji_id = str(entry.get("emoji_id", "")).strip()
        name     = str(entry.get("discord_name") or entry.get("key") or "").strip()
        key      = str(entry.get("key") or name).strip().lower()
        animated = entry.get("animated", False)
        if not emoji_id or not name:
            continue
        prefix = "a" if animated else ""
        tag    = f"<{prefix}:{name}:{emoji_id}>" if prefix else f"<:{name}:{emoji_id}>"
        lookup[key] = tag
        lookup[name.lower()] = tag

    def replace(m: re.Match) -> str:
        k = m.group(1).strip().lower()
        return lookup.get(k, m.group(0))

    return re.sub(r"\[\[([A-Za-z0-9_]+)\]\]", replace, text)
