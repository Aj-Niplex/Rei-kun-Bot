from __future__ import annotations

import ast
import importlib
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from discord.ext import commands

from .config_loader import BOT_ADMIN_USERS, BOT_ADMIN_USER_IDS


BACKUP_DIR = Path(".rei_backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST_FILE = BACKUP_DIR / "manifest.json"

DEPENDENCY_RELOADS: dict[str, list[str]] = {
    "utils.ai": ["commands.ai"],
    "utils.concurrency": ["commands.ai"],
    "utils.conversation": ["commands.ai"],
    "utils.emoji_assets": ["commands.ai"],
}

COMMON_RULES: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"async\s+with\s+await\s+aiohttp\.ClientSession\(\)\s+as\s+session\s*:"),
        "async with aiohttp.ClientSession() as session:",
        "Removed invalid await from ClientSession.",
    ),
    (
        re.compile(r"\bawait\s+aiohttp\.ClientSession\(\)"),
        "aiohttp.ClientSession()",
        "Removed invalid await from ClientSession.",
    ),
    (
        re.compile(r"\bawait\s+get_session\(\)"),
        "get_session()",
        "Removed invalid await from get_session().",
    ),
    (
        re.compile(r"\bawait\s+check_user_cooldown\(\s*([^,\n()]+)\s*,\s*[^)\n]+\)"),
        r"check_user_cooldown(\1)",
        "Removed extra cooldown argument.",
    ),
    (
        re.compile(r"utils/([A-Za-z0-9_]+)"),
        r"utils.\1",
        "Converted slash path to dot path.",
    ),
]


@dataclass
class Finding:
    line: Optional[int]
    severity: str
    title: str
    detail: str


@dataclass
class PatchPlan:
    patched_source: str
    changes: int
    notes: list[str]


def _load_manifest() -> dict:
    if not MANIFEST_FILE.exists():
        return {}
    try:
        return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_manifest(data: dict) -> None:
    MANIFEST_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def make_backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{path.stem}.{stamp}{path.suffix}.bak"
    shutil.copy2(path, backup_path)

    manifest = _load_manifest()
    manifest[str(path.resolve())] = {
        "backup": str(backup_path.resolve()),
        "time": stamp,
    }
    _save_manifest(manifest)
    return backup_path


def rollback_file(path: Path) -> Path:
    manifest = _load_manifest()
    key = str(path.resolve())
    if key not in manifest:
        raise FileNotFoundError("No backup found for this file.")

    backup_path = Path(manifest[key]["backup"])
    if not backup_path.exists():
        raise FileNotFoundError("Backup file missing.")

    shutil.copy2(backup_path, path)
    return backup_path


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def resolve_target(raw: str) -> Path | None:
    raw = (raw or "").strip().strip('"').strip("'")
    if not raw:
        return None

    p = Path(raw)
    if p.exists() and p.is_file():
        return p

    base = raw.replace("\\", "/")
    if base.endswith(".py"):
        base = base[:-3]
    base = base.replace("/", ".")

    candidates: list[Path] = []
    for root in ("commands", "utils"):
        candidates.append(Path(f"{root}/{base.split('.')[-1]}.py"))
        if base.startswith(f"{root}."):
            candidates.append(Path(base.replace(".", "/") + ".py"))

    for c in candidates:
        if c.exists() and c.is_file():
            return c

    return None


def path_to_module(path: Path) -> Optional[str]:
    parts = path.with_suffix("").parts
    for root in ("commands", "utils"):
        if root in parts:
            idx = parts.index(root)
            return ".".join(parts[idx:])
    return None


def scan_source(source: str) -> list[Finding]:
    findings: list[Finding] = []

    try:
        ast.parse(source)
    except SyntaxError as e:
        findings.append(Finding(e.lineno, "error", "SyntaxError", e.msg))
        return findings

    for i, line in enumerate(source.splitlines(), start=1):
        s = line.strip()

        if "await aiohttp.ClientSession()" in s:
            findings.append(Finding(i, "error", "Invalid await on ClientSession", "ClientSession() is not awaitable."))
        if "async with await aiohttp.ClientSession()" in s:
            findings.append(Finding(i, "error", "Invalid async with syntax", "Use async with aiohttp.ClientSession() as session."))
        if "await get_session()" in s:
            findings.append(Finding(i, "error", "Await on sync helper", "Remove await from get_session()."))
        if "await check_user_cooldown(" in s and "," in s:
            findings.append(Finding(i, "error", "Cooldown call has extra argument", "check_user_cooldown() appears to take 1 argument."))
        if "utils/" in s:
            findings.append(Finding(i, "warn", "Slash path detected", "Use dot notation like utils.ai."))

    if not findings:
        findings.append(Finding(None, "info", "No obvious static issues found", "Syntax and common scans passed."))

    return findings


def apply_safe_patches(source: str) -> PatchPlan:
    patched = source
    total = 0
    notes: list[str] = []

    for pattern, replacement, note in COMMON_RULES:
        patched, n = pattern.subn(replacement, patched)
        if n:
            total += n
            notes.append(f"{note} ({n} match(es))")

    return PatchPlan(patched_source=patched, changes=total, notes=notes)


async def reload_related(bot: commands.Bot, module: str) -> list[tuple[str, bool, str]]:
    importlib.invalidate_caches()
    targets = [module] + DEPENDENCY_RELOADS.get(module, [])
    results: list[tuple[str, bool, str]] = []

    for mod in targets:
        try:
            if mod.startswith("commands."):
                try:
                    await bot.reload_extension(mod)
                except commands.ExtensionNotLoaded:
                    await bot.load_extension(mod)
            else:
                if mod in sys.modules:
                    importlib.reload(sys.modules[mod])
                else:
                    importlib.import_module(mod)
            results.append((mod, True, ""))
        except Exception as e:
            results.append((mod, False, str(e)))

    return results


def build_report(source: str, filename: str, note: str = "") -> tuple[str, list[Finding], PatchPlan]:
    findings = scan_source(source)
    patch_plan = apply_safe_patches(source)

    risk = 0
    for f in findings:
        if f.severity == "error":
            risk += 3
        elif f.severity == "warn":
            risk += 1

    report = [
        "Reload Doctor Report",
        f"File: {filename}",
        f"Note: {note}" if note else "",
        f"Risk score: {risk}",
        f"Suggested replacements: {patch_plan.changes}",
        "",
        "Findings:",
    ]

    for f in findings:
        where = f"line {f.line}" if f.line else "summary"
        report.append(f"- [{f.severity.upper()}] {where}: {f.title} — {f.detail}")

    report.append("")
    report.append("Patch notes:")
    if patch_plan.notes:
        report.extend(f"- {n}" for n in patch_plan.notes)
    else:
        report.append("- No safe auto-patches detected.")

    return "\n".join(report), findings, patch_plan
