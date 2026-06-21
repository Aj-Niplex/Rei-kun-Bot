
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

DATA_DIR = Path("data")
RESOURCE_FILE = DATA_DIR / "resources.json"
RESOURCE_INDEX_FILE = DATA_DIR / "resource_index.json"

CODE_RE = re.compile(
    r"^BR\$(?P<subject>[A-Z0-9]{2,12})#C(?P<chapter>\d+)@V(?P<video>\d+)!(?P<hash>[A-Za-z0-9#$=@]{6,32})$"
)

def ensure_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for path, default in (
        (RESOURCE_FILE, {}),
        (RESOURCE_INDEX_FILE, {}),
    ):
        if not path.exists():
            path.write_text(json.dumps(default, indent=2, ensure_ascii=False), encoding="utf-8")

def _load(path: Path, default: Any):
    ensure_files()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
    except Exception:
        return default

def _save(path: Path, data: Any) -> None:
    ensure_files()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def load_resources() -> dict[str, dict[str, Any]]:
    data = _load(RESOURCE_FILE, {})
    return data if isinstance(data, dict) else {}

def save_resources(data: dict[str, dict[str, Any]]) -> None:
    _save(RESOURCE_FILE, data)

def load_index() -> dict[str, str]:
    data = _load(RESOURCE_INDEX_FILE, {})
    return data if isinstance(data, dict) else {}

def save_index(data: dict[str, str]) -> None:
    _save(RESOURCE_INDEX_FILE, data)

def parse_code(code: str) -> dict[str, Any | None]:
    code = (code or "").strip()
    m = CODE_RE.match(code)
    if not m:
        return None
    d = m.groupdict()
    d["code"] = code
    d["subject"] = d["subject"].upper().strip()
    d["chapter"] = int(d["chapter"])
    d["video"] = int(d["video"])
    return d

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip()).lower()

def extract_number(text: str) -> int | None:
    digits = "".join(ch for ch in str(text) if ch.isdigit())
    return int(digits) if digits else None

def build_code(subject: str, chapter: int, video: int, rand_hash: str) -> str:
    subject = re.sub(r"[^A-Z0-9]", "", str(subject).upper())[:12] or "XX"
    return f"BR${subject}#C{int(chapter)}@V{int(video)}!{rand_hash}"

def chapter_key(subject: str, chapter: str | int) -> str:
    return f"{normalize_text(subject)}|{extract_number(chapter) or chapter}"

def make_index_entry(record: dict[str, Any]) -> str:
    return chapter_key(record.get("subject", ""), record.get("chapter", ""))

def is_code_message(text: str) -> bool:
    return parse_code(text) is not None
