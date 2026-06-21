# Python 3.13 — Central emoji helper
import json
from pathlib import Path
from utils.config_loader import EMOJI_CATALOG_FILE

FALLBACK: dict[str, str] = {
    "success":"✅","error":"❌","warning":"⚠️","info":"ℹ️",
    "loading":"🔄","online":"🟢","ping":"🏓","star":"⭐",
    "flower":"🌸","flower_2":"🌸","crown":"👑","throne":"👑","ribbon":"🎀","butterfly":"🦋","butterfly_2":"🦋",
    "sparkle":"✨","paws":"🐾","gojo":"🥷","memory":"💾",
    "resource":"📚","reload":"♻️","admin":"🔒","dev":"⚙️",
    "char":"🎭","heart":"💜","violet_heart":"💜","bat":"🦇","cat":"🐱",
    "frustrated":"😤","missing":"❓","irritated":"😒","clapping_cat":"👏","crying_cat":"😭",
    "shocked_cat":"😱","happy_cat":"😺","sad_cat":"🙁","angry_cat":"😠","candy_man":"🍬",
    "clouds_or_dreaming":"☁️","spinning":"🌀","dead_flower":"🥀","footsteps":"👣",
    "blue_bird":"🐦","blue_flame":"🔥","wonderful":"🌟","kidding":"🤪","silence":"🤫",
    "crying":"😭","domain_expansion":"🫸","cool":"😎","dance":"💃","love":"🤍","wtf":"😵",
    "dev":"⚙️","bot":"🤖"
}


def _catalog() -> list[dict]:
    p = Path(EMOJI_CATALOG_FILE)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def E(name: str) -> str:
    """
    Return custom emoji tag. Tries:
      1. Pre-built 'tag' field in catalog (exact key/discord_name match)
      2. Partial name match
      3. Unicode fallback
    """
    key = name.lower().strip()
    for entry in _catalog():
        if not isinstance(entry, dict):
            continue
        entry_key  = str(entry.get("key","")).lower()
        entry_name = str(entry.get("discord_name","")).lower()
        if key in (entry_key, entry_name):
            t = entry.get("tag","")
            if t: return t
            # rebuild if tag field missing
            return _build(entry)

    # partial match
    for entry in _catalog():
        if not isinstance(entry, dict):
            continue
        ek = str(entry.get("key","")).lower()
        en = str(entry.get("discord_name","")).lower()
        if key in ek or key in en or ek in key:
            t = entry.get("tag","")
            if t: return t
            return _build(entry)

    return FALLBACK.get(key, "")


def _build(entry: dict) -> str:
    eid  = str(entry.get("emoji_id","")).strip()
    name = str(entry.get("discord_name") or entry.get("key","")).strip()
    anim = bool(entry.get("animated"))
    if not eid or not name:
        return ""
    return f"<a:{name}:{eid}>" if anim else f"<:{name}:{eid}>"


def tag(discord_name: str, emoji_id: str, animated: bool = False) -> str:
    return f"<a:{discord_name}:{emoji_id}>" if animated else f"<:{discord_name}:{emoji_id}>"


def all_tags() -> list[str]:
    seen: set[str] = set()
    result = []
    for e in _catalog():
        eid = str(e.get("emoji_id",""))
        if eid in seen: continue
        seen.add(eid)
        t = e.get("tag","") or _build(e)
        if t: result.append(t)
    return result
