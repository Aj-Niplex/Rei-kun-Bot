# Python 3.13 — Central config loader from environment
import os
from dotenv import load_dotenv

load_dotenv()

# Core
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

def _parse_model_list(raw: str | None) -> list[str]:
    """Parse comma-separated model list from env."""
    if not raw:
        return ["openrouter/auto"]
    return [m.strip() for m in raw.split(",") if m.strip()]

OPENROUTER_MODELS = _parse_model_list(os.getenv("OPENROUTER_MODELS", "openrouter/auto"))

# Bot Identity
PREFIX = os.getenv("BOT_PREFIX", "?").strip() or "?"
BOT_VERSION = os.getenv("BOT_VERSION", "v6.0.0")
BOT_DEV = os.getenv("BOT_DEV", "@dora_aj")

# Files
EMOJI_CATALOG_FILE = os.getenv("EMOJI_CATALOG_FILE", "ai/knowledge/emoji_catalog.json").strip()
SYSTEM_PROMPT_FILE = os.getenv("SYSTEM_PROMPT_FILE", "ai/system prompt.txt").strip()

# Access Control
def _csv(val: str | None) -> set[str]:
    if not val:
        return set()
    return {x.strip() for x in val.split(",") if x.strip()}

BOT_ADMIN_USERS = {x.lower() for x in _csv(os.getenv("BOT_ADMIN_USERS", "dora_aj"))}
BOT_ADMIN_USER_IDS = _csv(os.getenv("BOT_ADMIN_USER_IDS", "1489553674287054848"))
BOT_OWNER_USER_IDS = _csv(os.getenv("BOT_OWNER_USER_IDS", "1489553674287054848"))

# Resource Hub
RESOURCE_TRIGGER_CHANNEL_ID = int(os.getenv("RESOURCE_TRIGGER_CHANNEL_ID", "0") or 0)
RESOURCE_NOTIFY_USER_ID = int(os.getenv("RESOURCE_NOTIFY_USER_ID", "0") or 0)
RESOURCE_ALLOWED_USER_IDS = _csv(os.getenv("RESOURCE_ALLOWED_USER_IDS", ""))
RESOURCE_ALLOWED_ROLE_IDS = _csv(os.getenv("RESOURCE_ALLOWED_ROLE_IDS", ""))
RESOURCE_ALLOW_ADMINISTRATOR = os.getenv("RESOURCE_ALLOW_ADMINISTRATOR", "true").lower() in {"1", "true", "yes"}

# Error Handler
ERROR_HANDLER_ENABLED = os.getenv("ERROR_HANDLER_ENABLED", "true").lower() in {"1", "true", "yes"}
ERROR_REPORT_EMAIL = os.getenv("ERROR_REPORT_EMAIL", "mind87353@gmail.com").strip()

def load_env():
    """Return full environment dict for modules that need extra vars."""
    return dict(os.environ)
