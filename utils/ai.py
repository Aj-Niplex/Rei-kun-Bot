# Python 3.13 | discord.py 2.6.4
# Fixed: identity priming, conversation history, better model order
from pathlib import Path
from utils.emoji_parser import parse_emojis
from utils.emoji_assets import build_emoji_context, render_asset_placeholders
from utils.storage import build_memory_context
from utils.concurrency import get_session, AI_SEMAPHORE, inc_active, dec_active
from utils.conversation import get_history, add_message
from utils.config_loader import OPENROUTER_API_KEY, OPENROUTER_MODELS, SYSTEM_PROMPT_FILE

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# 🔒 Try to load from hardcoded system_prompt.py first (if it exists)
# Falls back to traditional .txt file if the new system isn't in place
try:
    from core.system_prompt import get_system_prompt
    USE_LOCKED_PROMPT = True
except ImportError:
    USE_LOCKED_PROMPT = False

SYSTEM_PROMPT_PATHS: list[Path] = [
    Path(SYSTEM_PROMPT_FILE),
    Path("ai/system prompt.txt"),
    Path("ai/system_prompt.txt"),
]
BOT_HELP_FILE    = Path("ai/knowledge/bot_help.txt")
VERSION_LOG_FILE = Path("ai/knowledge/version_log_v1.txt")

# ── Identity seed ─────────────────────────────────────────────────────
# Forces the model to establish Rei-kun identity before any conversation.
# This "primes" even models that fight system prompts.
IDENTITY_SEED = [
    {
        "role": "user",
        "content": "Who are you and who made you?",
    },
    {
        "role": "assistant",
        "content": (
            "I'm Rei-kun! A Discord bot built by @dora_aj (Adarsh). "
            "I'm trained on Mis. ERICA-SAN's persona, so I've got a little personality [[flower]] "
            "I'm here to help with AI, server stuff, translations, and more. What's up?"
        ),
    },
]

# ── Better model order — identity-respecting models first ─────────────
# Models now loaded from .env (OPENROUTER_MODELS)
IDENTITY_FRIENDLY_MODELS: list[str] = OPENROUTER_MODELS or [
    "openrouter/auto",
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-3.3-70b:free",
]


def _read_first(paths: list[Path]) -> str:
    # 🔒 If locked system prompt exists, use it instead of .txt file
    if USE_LOCKED_PROMPT:
        try:
            return get_system_prompt()
        except Exception as e:
            print(f"[AI] ⚠️ Failed to load locked system prompt: {e}, falling back to .txt")
    
    # Fallback to traditional .txt file loading
    for p in paths:
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except Exception:
                pass
    return ""


def _intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["version", "update", "changelog", "what changed"]):
        return "version"
    if any(k in t for k in ["help", "command", "how to use", "botinfo"]):
        return "bot_help"
    if any(k in t for k in ["memory", "remember", "saved", "birthday"]):
        return "memory"
    return "general"


async def _call(
    model: str,
    system: str,
    messages: list[dict],
) -> tuple[str | None, str | None]:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "http://localhost",
        "X-Title":       "Rei-kun",
    }
    payload = {
        "model":    model,
        "messages": [{"role": "system", "content": system}] + messages,
        "temperature": 0.75,
    }

    session = get_session()
    try:
        async with session.post(OPENROUTER_URL, headers=headers, json=payload) as resp:
            raw = await resp.text()
            try:
                data = await resp.json(content_type=None)
            except Exception:
                data = None
            if resp.status != 200:
                return None, f"HTTP {resp.status}: {(str(data) or raw)[:300]}"
            if not isinstance(data, dict):
                return None, f"Bad response: {raw[:300]}"
            try:
                return data["choices"][0]["message"]["content"], None
            except Exception:
                return None, f"Parse error: {data}"
    except Exception as e:
        return None, f"Request error: {e}"


async def ask_ai(
    prompt: str,
    guild_id: int | str | None = None,
    channel_id: int | str | None = None,
    author_name: str = "",
) -> str:
    """
    Full AI call with:
    - Identity seed (forces Rei-kun persona even on stubborn models)
    - Conversation history (AI remembers previous messages in channel)
    - Shared HTTP session + semaphore
    """
    if not OPENROUTER_API_KEY:
        return "OpenRouter API key missing."

    system_prompt = _read_first(SYSTEM_PROMPT_PATHS)
    memory        = build_memory_context(guild_id) if guild_id else "No saved memory."
    bot_help      = BOT_HELP_FILE.read_text(encoding="utf-8")    if BOT_HELP_FILE.exists()    else ""
    version_log   = VERSION_LOG_FILE.read_text(encoding="utf-8") if VERSION_LOG_FILE.exists() else ""
    emoji_ctx     = ""

    if any(k in prompt.lower() for k in ["emoji", "gif", "react", "sticker", "custom"]):
        emoji_ctx = build_emoji_context(max_items=60)

    # Build system prompt
    system = system_prompt or "You are Rei-kun, a Discord bot made by @dora_aj."
    system += f"\n\nSERVER MEMORY:\n{memory}"
    if bot_help:
        system += f"\n\nBOT HELP:\n{bot_help}"
    if version_log:
        system += f"\n\nVERSION LOG:\n{version_log}"
    if emoji_ctx:
        system += f"\n\nCUSTOM EMOJIS (use [[key]] placeholders):\n{emoji_ctx}"
    
    history = get_history(channel_id) if channel_id else []
    user_msg = {"role": "user", "content": prompt}

    messages = IDENTITY_SEED + history + [user_msg]

    if author_name:
        messages = IDENTITY_SEED + [
            {
                "role": "user",
                "content": f"The current user is: {author_name}. Remember this name when replying."
            }
        ] + history + [user_msg]

    # Use identity-friendly models first
    models   = IDENTITY_FRIENDLY_MODELS
    last_err = None

    async with AI_SEMAPHORE:
        await inc_active()
        try:
            for model in models:
                try:
                    print(f"[AI] Trying: {model}")
                    result, err = await _call(model, system, messages)
                    if result:
                        print(f"[AI] ✅ {model}")
                        final = parse_emojis(render_asset_placeholders(result))
                        # Save to conversation history
                        if channel_id:
                            add_message(channel_id, "user",      prompt)
                            add_message(channel_id, "assistant", result)  # raw, before emoji parse
                        return final
                    last_err = err
                    print(f"[AI] ❌ {model} | {err}")
                except Exception as e:
                    last_err = str(e)
                    print(f"[AI] 💥 {model} | {e}")
        finally:
            await dec_active()

    return f"All AI models failed.\nLast error: {last_err}"
 
