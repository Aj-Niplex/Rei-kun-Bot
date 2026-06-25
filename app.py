# Python 3.13 | discord.py 2.6.4
import asyncio
import logging
import platform
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands

from utils.config_loader import (
    BOT_ADMIN_USER_IDS,
    BOT_ADMIN_USERS,
    BOT_VERSION,
    DISCORD_TOKEN,
    PREFIX,
)
from utils.logger import log_event
from utils.message_utils import send_discord_text
from utils.permissions import is_allowed_dm_user
from utils.storage import ensure_storage, is_user_blocked
from utils.activity_logger import ActivityLogger
from utils.ai_monitor import AIMonitor
from utils.interaction_tracker import set_activity_logger

logging.getLogger("discord").setLevel(logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True


def _prefixes(bot: commands.Bot, message: discord.Message) -> list[str]:
    base = (PREFIX or "?").strip() or "?"
    return [base, base + " ", base + "  "]


bot = commands.Bot(
    command_prefix=_prefixes,
    intents=intents,
    help_command=None,
    case_insensitive=True,
)

# Initialize Advanced Activity Logger & AI Monitor
activity_logger = None
ai_monitor = None


def _iter_command_modules() -> list[str]:
    cmd_dir = Path("commands")
    if not cmd_dir.exists():
        return []
    return [
        f"commands.{f.stem}"
        for f in sorted(cmd_dir.iterdir())
        if f.suffix == ".py" and f.name != "__init__.py"
    ]


def _is_admin(author: discord.abc.User) -> bool:
    return (
        str(author.id) in BOT_ADMIN_USER_IDS
        or str(getattr(author, "name", "")).lower() in {x.lower() for x in BOT_ADMIN_USERS}
    )


AI_COMMANDS = {"ai", "aihelp"}
DELETE_COMMANDS = {
    "reload", "ping", "quote", "topic", "save", "remember",
    "tell", "tr", "fix", "botinfo", "userid", "botblock",
    "botunblock", "promote", "demote", "admins",
}

# ── ToS gate ──────────────────────────────────────────────────────────
BYPASS_COMMANDS = {"tos", "agree"}   # commands that skip ToS check


async def _tos_gate(message: discord.Message, cmd: str) -> bool:
    """
    Returns True if the user may proceed.
    Returns False if blocked by ToS (message already handled).
    Admins always bypass.
    """
    from utils.tos import has_agreed, mark_agreed, increment_attempts, MAX_ATTEMPTS
    from utils.storage import block_user
    from utils import embeds as emb

    if _is_admin(message.author):
        return True
    if cmd in BYPASS_COMMANDS:
        return True

    uid = str(message.author.id)
    if has_agreed(uid):
        return True

    try:
        tos_msg = await message.channel.send(embed=emb.tos_embed(message.author))
        await tos_msg.add_reaction("👍")
        await tos_msg.add_reaction("👎")

        def check(reaction, user):
            return (
                user == message.author
                and reaction.message.id == tos_msg.id
                and str(reaction.emoji) in ("👍", "👎")
            )

        try:
            reaction, _ = await bot.wait_for("reaction_add", timeout=60, check=check)
        except asyncio.TimeoutError:
            await tos_msg.edit(content="", embed=emb.tos_timeout_embed(message.author))
            increment_attempts(uid)
            return False

        if str(reaction.emoji) == "👍":
            mark_agreed(uid)
            await tos_msg.edit(content="", embed=emb.tos_agreed_embed(message.author))
            return True
        else:
            attempts = increment_attempts(uid)
            remaining = MAX_ATTEMPTS - attempts
            if remaining <= 0:
                block_user(uid)
            await tos_msg.edit(content="", embed=emb.tos_declined_embed(message.author, remaining))
            return False

    except Exception:
        return True


@bot.event
async def setup_hook() -> None:
    global activity_logger, ai_monitor
    ensure_storage()
    
    # Initialize Activity Logger
    activity_logger = ActivityLogger(bot)
    set_activity_logger(activity_logger)
    
    # Get owner ID (first admin ID)
    owner_id = int(list(BOT_ADMIN_USER_IDS)[0]) if BOT_ADMIN_USER_IDS else 0
    
    # Initialize AI Monitor
    ai_monitor = AIMonitor(bot, activity_logger, owner_id)
    
    # Load prefix commands (DISABLED - now using slash commands only)
    # Keeping prefix commands for backward compatibility, but slash is primary
    for module_name in _iter_command_modules():
        try:
            await bot.load_extension(module_name)
            print(f"[LOAD] ✅ {module_name} (prefix backup)")
        except Exception as e:
            print(f"[LOAD] ❌ {module_name}: {e}")
    
    # Slash commands removed - using prefix commands only (! and ?)
    
    # Sync slash commands to Discord (THIS MAKES THEM APPEAR IN THE PANEL!)
    try:
        synced = await bot.tree.sync()
        print(f"[SYNC] ✅ Synced {len(synced)} slash command(s) to Discord")
        print("[INFO] 🎮 Type '/' in Discord to see your bot's commands!")
    except Exception as e:
        print(f"[SYNC] ❌ Failed to sync slash commands: {e}")


@bot.event
async def on_ready() -> None:
    global ai_monitor
    ist = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %I:%M:%S %p IST")
    total_users = sum(g.member_count or 0 for g in bot.guilds)
    sep = "=" * 54
    print(sep)
    print(f"🤖 Rei-kun {BOT_VERSION}")
    print(sep)
    print(f"👤 Logged in as : {bot.user}")
    print(f"🆔 Bot ID       : {bot.user.id if bot.user else 'unknown'}")
    print(f"⚡ Prefix       : {PREFIX}")
    print(f"🐍 Python       : {platform.python_version()}")
    print(f"🧠 discord.py   : {discord.__version__}")
    print(f"🌐 Servers      : {len(bot.guilds)}")
    print(f"👥 Users        : {total_users}")
    print(f"🕒 Started At   : {ist}")
    print(sep)
    print("✅ Rei-kun is now ONLINE")
    print(sep)
    
    # Start AI Monitor
    if ai_monitor:
        await ai_monitor.start_monitoring()
        print("[AI_MONITOR] 🔍 Started background monitoring")


@bot.event
async def on_interaction(interaction: discord.Interaction) -> None:
    """Track all interactions (slash commands)."""
    global activity_logger
    if interaction.type == discord.InteractionType.application_command:
        if activity_logger:
            activity_logger.log_command_start(interaction)


@bot.event
async def on_message(message: discord.Message) -> None:
    global activity_logger
    if message.author.bot:
        return

    # Log incoming message
    if activity_logger:
        activity_logger.log_message(message)

    in_dm = message.guild is None

    if in_dm and not is_allowed_dm_user(message.author, BOT_ADMIN_USERS, BOT_ADMIN_USER_IDS):
        return

    if not in_dm and is_user_blocked(str(message.author.id)):
        return

    content = message.content.strip()
    base = (PREFIX or "?").strip() or "?"
    if not content.startswith(base):
        await bot.process_commands(message)
        return

    cmd = content[len(base):].lstrip().split(maxsplit=1)[0].lower() if content[len(base):].strip() else ""
    if not cmd:
        await bot.process_commands(message)
        return

    # ── ToS check ──
    if not _is_admin(message.author) and not in_dm:
        allowed = await _tos_gate(message, cmd)
        if not allowed:
            return

    await bot.process_commands(message)

    log_event(
        f"USER={message.author} ID={message.author.id} "
        f"SERVER={getattr(message.guild, 'name', 'DM')} "
        f"CHANNEL={getattr(message.channel, 'name', str(message.channel))} "
        f"CMD={content}"
    )

    if cmd in AI_COMMANDS:
        return

    if cmd in DELETE_COMMANDS:
        try:
            await message.delete()
        except Exception:
            pass


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    raw = str(error)
    from utils.bot_emojis import E
    from utils.config_loader import ERROR_HANDLER_ENABLED, ERROR_REPORT_EMAIL

    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"{E('error')} Missing required argument.", mention_author=False)
        return
    if isinstance(error, commands.BadArgument):
        await ctx.reply(f"{E('error')} Bad argument provided.", mention_author=False)
        return

    api_keywords = ("401", "403", "404", "429", "openrouter", "unauthorized", "rate limit")
    if any(k in raw.lower() for k in api_keywords):
        log_event(f"API_ERROR user={ctx.author} cmd={ctx.message.content} err={raw}")
        await send_discord_text(ctx, f"{E('error')} API Error:\n```{raw}```", reply=True, mention_author=False)
        return

    log_event(f"ERROR user={ctx.author} cmd={ctx.message.content} err={raw}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AI-POWERED ERROR HANDLER + EMAIL REPORTING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Get detailed error info
    import traceback as tb_module
    error_traceback = "".join(tb_module.format_exception(type(error), error, error.__traceback__))
    
    # Determine which file caused the error
    file_path = "unknown"
    if error.__traceback__:
        tb = error.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        file_path = tb.tb_frame.f_code.co_filename
    
    # Build context for AI
    user_info = f"{ctx.author} (ID: {ctx.author.id})"
    guild_info = f"{ctx.guild.name} (ID: {ctx.guild.id})" if ctx.guild else "DM"
    channel_info = f"#{ctx.channel.name}" if hasattr(ctx.channel, 'name') else str(ctx.channel)
    command_used = ctx.message.content
    
    # Ask AI to diagnose and format as email (structured in 3 sections)
    from utils.ai import ask_ai
    
    # Section 1: AI Explanation
    explanation_prompt = f"""You are analyzing a Discord bot error. Explain what went wrong in simple, technical terms.

ERROR TYPE: {type(error).__name__}
ERROR MESSAGE: {raw}
COMMAND: {command_used}
FILE: {file_path}

TRACEBACK:
{error_traceback}

Explain:
1. What is this error type?
2. What exactly caused it in this context?
3. Why did it happen?

Keep it clear and concise. Use HTML formatting (<p>, <strong>, <code>, <ul>, <li>)."""

    ai_explanation = await ask_ai(explanation_prompt, guild_id=(ctx.guild.id if ctx.guild else "dm"))
    
    # Section 2: Temporary Fix
    temp_fix_prompt = f"""Based on this error, suggest a QUICK TEMPORARY FIX the developer can do RIGHT NOW to keep the bot working.

ERROR: {type(error).__name__} in {file_path}
MESSAGE: {raw}

Provide:
1. What to do IMMEDIATELY (comment out code, add try/except, change a value, etc.)
2. Why this temporary fix will work
3. Warning that this is NOT a permanent solution

Be specific. Use HTML formatting (<p>, <strong>, <code>, <ol>, <li>). Keep it short."""

    temp_fix = await ask_ai(temp_fix_prompt, guild_id=(ctx.guild.id if ctx.guild else "dm"))
    
    # Section 3: AI Coder Prompt (copy-paste ready)
    ai_coder_prompt = f"""Fix this error in my Discord bot file.

FILE: {file_path}
ERROR TYPE: {type(error).__name__}
ERROR MESSAGE: {raw}

TRACEBACK:
{error_traceback}

CONTEXT:
- Command: {command_used}
- User: {user_info}
- Server: {guild_info}

Please:
1. Identify the exact line causing the error
2. Explain what's wrong
3. Provide the corrected version of the ENTIRE file with proper error handling
4. Add comments explaining the fix

Make sure the fix handles edge cases and doesn't break other functionality."""
    
    # Send email report to owner (if enabled)
    if ERROR_HANDLER_ENABLED and ERROR_REPORT_EMAIL:
        try:
            from utils.email_sender import send_error_email, format_error_report_html
            
            # Simple summary for email body
            simple_summary = f"""🚨 Error Detected in Rei-kun Bot

Error Type: {type(error).__name__}
File: {file_path}
Command: {command_used}

Quick Summary:
{raw[:200]}{'...' if len(raw) > 200 else ''}

📎 Open the attached HTML file for complete diagnostic details, AI analysis, and fix suggestions."""
            
            # Detailed HTML attachment with structured AI sections
            detailed_html = format_error_report_html(
                error_type=type(error).__name__,
                error_message=raw,
                command=command_used,
                user=user_info,
                guild=guild_info,
                channel=channel_info,
                file_path=file_path,
                traceback=error_traceback,
                ai_explanation=ai_explanation,
                temp_fix=temp_fix,
                ai_prompt=ai_coder_prompt
            )
            
            subject = f"🚨 Rei-kun Error: {type(error).__name__} in {file_path.split('/')[-1]}"
            success, msg = await send_error_email(subject, simple_summary, detailed_html)
            
            if success:
                print(f"[ERROR_HANDLER] ✅ Email sent to {ERROR_REPORT_EMAIL}")
            else:
                print(f"[ERROR_HANDLER] ❌ Email failed: {msg}")
        
        except Exception as e:
            print(f"[ERROR_HANDLER] ❌ Email system error: {e}")
    
    # Reply to user with SHORT message (full diagnosis goes to email only)
    user_message = f"{E('error')} **Oops! Something went wrong.**\n\n{E('mail')} Don't worry - I've sent a detailed error report to the owner. They'll investigate and fix this soon!\n\n*Error type: `{type(error).__name__}`*"
    
    await send_discord_text(ctx, user_message, reply=True, mention_author=False)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    """Global error handler for slash commands."""
    global activity_logger
    raw = str(error)
    from utils.bot_emojis import E
    from utils.config_loader import ERROR_HANDLER_ENABLED, ERROR_REPORT_EMAIL
    
    # Skip common non-critical errors
    if isinstance(error, app_commands.CommandNotFound):
        return
    if isinstance(error, app_commands.MissingPermissions):
        return await interaction.response.send_message(
            f"{E('error')} You don't have permission to use this command.",
            ephemeral=True
        )
    
    # Log the error to activity logger
    if activity_logger:
        activity_logger.log_command_error(interaction, error)
    
    # Log the error
    log_event(f"SLASH_ERROR user={interaction.user} cmd=/{interaction.command.name if interaction.command else 'unknown'} err={raw}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AI-POWERED ERROR HANDLER + EMAIL REPORTING (SLASH COMMANDS)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Get detailed error info
    import traceback as tb_module
    error_traceback = "".join(tb_module.format_exception(type(error), error, error.__traceback__))
    
    # Determine which file caused the error
    file_path = "unknown"
    if error.__traceback__:
        tb = error.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        file_path = tb.tb_frame.f_code.co_filename
    
    # Build context for AI
    user_info = f"{interaction.user} (ID: {interaction.user.id})"
    guild_info = f"{interaction.guild.name} (ID: {interaction.guild.id})" if interaction.guild else "DM"
    channel_info = f"#{interaction.channel.name}" if hasattr(interaction.channel, 'name') else str(interaction.channel)
    command_used = f"/{interaction.command.name}" if interaction.command else "/unknown"
    
    # Ask AI to diagnose and format as email
    from utils.ai import ask_ai
    ai_prompt = f"""You are analyzing a Discord bot slash command error. Format your response as a professional error diagnosis.

ERROR TYPE: {type(error).__name__}
ERROR MESSAGE: {raw}
COMMAND: {command_used}
USER: {user_info}
SERVER: {guild_info}
CHANNEL: {channel_info}
FILE: {file_path}

TRACEBACK:
{error_traceback}

Provide:
1. Root cause (what went wrong)
2. Why it happened
3. How to fix it
4. Code suggestion if applicable

Keep it technical but clear."""

    explanation = await ask_ai(ai_prompt, guild_id=(interaction.guild.id if interaction.guild else "dm"))
    
    # Send email report to owner (if enabled)
    if ERROR_HANDLER_ENABLED and ERROR_REPORT_EMAIL:
        try:
            from utils.email_sender import send_error_email, format_error_report_html
            
            html_body = format_error_report_html(
                error_type=type(error).__name__,
                error_message=raw,
                command=command_used,
                user=user_info,
                guild=guild_info,
                channel=channel_info,
                file_path=file_path,
                traceback=error_traceback,
                ai_diagnosis=explanation
            )
            
            subject = f"🚨 Rei-kun Slash Command Error: {type(error).__name__} in {command_used}"
            success, msg = await send_error_email(subject, html_body)
            
            if success:
                print(f"[ERROR_HANDLER] ✅ Email sent to {ERROR_REPORT_EMAIL}")
            else:
                print(f"[ERROR_HANDLER] ❌ Email failed: {msg}")
        
        except Exception as e:
            print(f"[ERROR_HANDLER] ❌ Email system error: {e}")
    
    # Reply to user
    if "All AI models failed" in explanation or "OpenRouter API key" in explanation:
        user_message = f"{E('error')} **Something went wrong!**\n\n```{raw}```\n\n{E('mail')} I've sent a detailed error report to the owner. They'll fix this soon!"
    else:
        user_message = f"{E('error')} **Something went wrong!**\n\n{E('gojo')} {explanation}\n\n{E('mail')} A detailed error report has been sent to the owner. Please wait while they investigate and fix the issue!"
    
    # Check if we need to respond or followup
    try:
        if interaction.response.is_done():
            await interaction.followup.send(user_message, ephemeral=True)
        else:
            await interaction.response.send_message(user_message, ephemeral=True)
    except Exception:
        # If all else fails, just log it
        print(f"[ERROR_HANDLER] Could not send error message to user: {user_message}")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise SystemExit("Set DISCORD_TOKEN before running.")
    bot.run(DISCORD_TOKEN)
