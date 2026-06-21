
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path("data")
GUILDS_DIR = BASE_DIR / "guilds"
BLOCK_FILE = BASE_DIR / "blocked_users.json"

MEMORY_CATEGORIES = ("memories", "promises", "fights", "dates")


def ensure_storage() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    GUILDS_DIR.mkdir(parents=True, exist_ok=True)
    if not BLOCK_FILE.exists():
        BLOCK_FILE.write_text("[]", encoding="utf-8")


def get_guild_folder(guild_id) -> Path:
    ensure_storage()
    folder = GUILDS_DIR / str(guild_id)
    folder.mkdir(parents=True, exist_ok=True)
    for cat in MEMORY_CATEGORIES:
        file = folder / f"{cat}.json"
        if not file.exists():
            file.write_text("[]", encoding="utf-8")
    return folder


def guild_file(guild_id, category: str) -> Path:
    folder = get_guild_folder(guild_id)
    file = folder / f"{category}.json"
    if not file.exists():
        file.write_text("[]", encoding="utf-8")
    return file


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def load_list(path: Path) -> list[Any]:
    data = _load_json(path)
    return data if isinstance(data, list) else []


def save_list(path: Path, data: list[Any]) -> None:
    _save_json(path, data)


def save_memory(guild_id, category: str, text: str) -> None:
    path = guild_file(guild_id, category)
    data = load_list(path)
    data.append(text)
    save_list(path, data)


def get_memories(guild_id, category: str) -> list[Any]:
    path = guild_file(guild_id, category)
    return load_list(path)


def build_memory_context(guild_id, max_items_per_category: int = 6) -> str:
    ensure_storage()
    folder = get_guild_folder(guild_id)
    parts = []
    for category in MEMORY_CATEGORIES:
        path = folder / f"{category}.json"
        data = load_list(path)
        if data:
            recent = [str(x).strip() for x in data[-max_items_per_category:] if str(x).strip()]
            if recent:
                parts.append(f"{category.title()}:\n- " + "\n- ".join(recent))
    return "\n\n".join(parts) if parts else "No saved memories yet."


def is_user_blocked(user_id: str) -> bool:
    ensure_storage()
    data = load_list(BLOCK_FILE)
    user_id = str(user_id)
    return user_id in {str(x) for x in data}


def block_user(user_id: str) -> None:
    ensure_storage()
    data = load_list(BLOCK_FILE)
    uid = str(user_id)
    if uid not in {str(x) for x in data}:
        data.append(uid)
    save_list(BLOCK_FILE, data)


def unblock_user(user_id: str) -> None:
    ensure_storage()
    data = [str(x) for x in load_list(BLOCK_FILE) if str(x) != str(user_id)]
    save_list(BLOCK_FILE, data)
