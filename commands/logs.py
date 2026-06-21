from __future__ import annotations

import io
import math
from pathlib import Path

import discord
from discord.ext import commands

from utils.config_loader import BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS, BOT_OWNER_USER_IDS
from utils.bot_emojis import E

FOOTER = "Rei-kun Advanced Log Manager v3.0"

LOG_DIRS = [
    Path("logs"),
    Path("/home/container/logs"),
    Path("/home/container"),
]

LOG_PATTERNS = ("*.log", "*.txt")


def _is_admin(u: discord.abc.User) -> bool:
    return (
        str(u.id) in BOT_ADMIN_USER_IDS
        or str(getattr(u, "name", "")).lower() in {x.lower() for x in BOT_ADMIN_USERS}
    )


def _is_owner(u: discord.abc.User) -> bool:
    return str(u.id) in BOT_OWNER_USER_IDS


def _iter_log_files() -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []

    for base in LOG_DIRS:
        if not base.exists():
            continue
        for pattern in LOG_PATTERNS:
            for p in base.rglob(pattern):
                if p.is_file() and p not in seen:
                    seen.add(p)
                    out.append(p)

    return sorted(out)


def _collect_matches(user_id: str) -> list[str]:
    needles = (
        f"USER_ID={user_id}",
        f"USER_ID: {user_id}",
        f"USER ID={user_id}",
        f"USER ID: {user_id}",
        user_id,
    )

    matches: list[str] = []

    for file in _iter_log_files():
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line in text.splitlines():
            if any(n in line for n in needles):
                matches.append(f"[{file.name}] {line}")

    return matches


def _get_all_logs(limit: int = 100) -> list[str]:
    """Get recent logs from all log files."""
    all_lines: list[str] = []
    
    for file in _iter_log_files():
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()
            for line in lines[-limit:]:  # Get last N lines from each file
                all_lines.append(f"[{file.name}] {line}")
        except Exception:
            continue
    
    return all_lines[-limit:]  # Return most recent entries


def _get_vps_logs(limit: int = 50) -> list[str]:
    """Get VPS-specific logs."""
    vps_log = Path("logs/vps.log")
    if not vps_log.exists():
        return []
    
    try:
        text = vps_log.read_text(encoding="utf-8", errors="ignore")
        return text.splitlines()[-limit:]
    except Exception:
        return []


def _clear_user_logs(user_id: str) -> int:
    """Clear logs for a specific user. Returns number of lines removed."""
    removed = 0
    
    needles = (
        f"USER_ID={user_id}",
        f"USER_ID: {user_id}",
        f"USER ID={user_id}",
        f"USER ID: {user_id}",
        user_id,
    )
    
    for file in _iter_log_files():
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()
            
            # Filter out lines matching user_id
            new_lines = [line for line in lines if not any(n in line for n in needles)]
            removed += len(lines) - len(new_lines)
            
            # Write back
            file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        except Exception:
            continue
    
    return removed


def _clear_all_logs() -> int:
    """Clear all log files. Returns number of files cleared."""
    cleared = 0
    
    for file in _iter_log_files():
        try:
            file.write_text("", encoding="utf-8")
            cleared += 1
        except Exception:
            continue
    
    return cleared


async def setup(bot: commands.Bot) -> None:
    @bot.command(name="logs")
    async def logs_cmd(ctx: commands.Context, user_id: str = "", page: int = 1) -> None:
        """View user-specific logs or recent logs. User-specific logs require admin."""
        # If user_id provided, require admin. If not, anyone can see recent logs.
        if user_id and not _is_admin(ctx.author):
            return await ctx.send(f"{E('error')} Admin only for user-specific logs.")

        loading = await ctx.send(f"{E('loading')} Searching logs...")

        if not user_id:
            # Show recent logs from all files (public)
            entries = _get_all_logs(100)
            if not entries:
                return await loading.edit(content=f"{E('error')} No logs found.")
            
            per_page = 20
            total_pages = max(1, math.ceil(len(entries) / per_page))
            page = max(1, min(page, total_pages))
            
            start = (page - 1) * per_page
            chunk = entries[start : start + per_page]
            preview = "\n".join(chunk)
            
            embed = discord.Embed(
                title=f"{E('logs')} Recent Bot Logs",
                color=0x5865F2,
                description=f"```text\n{preview[:3500]}\n```",
            )
            embed.add_field(name="Total Entries", value=str(len(entries)), inline=True)
            embed.add_field(name="Page", value=f"{page}/{total_pages}", inline=True)
            embed.set_footer(text=f"{FOOTER} {E('ribbon')}")
            
            return await loading.edit(content="", embed=embed)

        # User-specific logs
        entries = _collect_matches(user_id)

        if not entries:
            return await loading.edit(content=f"{E('error')} No logs found for `{user_id}`.")

        per_page = 20
        total_pages = max(1, math.ceil(len(entries) / per_page))
        page = max(1, min(page, total_pages))

        start = (page - 1) * per_page
        chunk = entries[start : start + per_page]
        preview = "\n".join(chunk)

        embed = discord.Embed(
            title=f"{E('logs')} User Logs",
            color=0x5865F2,
            description=f"```text\n{preview[:3500]}\n```",
        )
        embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
        embed.add_field(name="Entries", value=str(len(entries)), inline=True)
        embed.add_field(name="Page", value=f"{page}/{total_pages}", inline=True)
        embed.set_footer(text=f"{FOOTER} {E('ribbon')}")

        buf = io.BytesIO()
        full_text = (
            f"User ID: {user_id}\n"
            f"Found entries: {len(entries)}\n"
            f"Page preview: {page}/{total_pages}\n\n"
            + "\n".join(entries)
        )
        buf.write(full_text.encode("utf-8"))
        buf.seek(0)

        await loading.edit(content="", embed=embed)
        await ctx.send(file=discord.File(buf, filename=f"logs_{user_id}.txt"))
    
    
    @bot.command(name="vpslogs", aliases=["vlog"])
    async def vps_logs_cmd(ctx: commands.Context, lines: int = 50) -> None:
        """View VPS logs. Owner only."""
        if not _is_owner(ctx.author):
            return await ctx.send(f"{E('error')} Owner only.")
        
        loading = await ctx.send(f"{E('loading')} Fetching VPS logs...")
        
        entries = _get_vps_logs(min(lines, 200))
        
        if not entries:
            return await loading.edit(content=f"{E('error')} No VPS logs found.")
        
        preview = "\n".join(entries[-50:])  # Show last 50 lines in embed
        
        embed = discord.Embed(
            title=f"{E('info')} VPS Logs",
            color=0x5865F2,
            description=f"```text\n{preview[:3500]}\n```",
        )
        embed.add_field(name="Total Lines", value=str(len(entries)), inline=True)
        embed.set_footer(text=f"{FOOTER} {E('ribbon')}")
        
        await loading.edit(content="", embed=embed)
    
    
    @bot.command(name="clearlogs")
    async def clear_logs_cmd(ctx: commands.Context, user_id: str = "") -> None:
        """Clear logs for a user (admin) or all logs (owner)."""
        # User-specific clear = admin. Clear ALL = owner only.
        if user_id and not _is_admin(ctx.author):
            return await ctx.send(f"{E('error')} Admin only for user-specific log clear.")
        
        if not user_id and not _is_owner(ctx.author):
            return await ctx.send(f"{E('error')} Owner only for clearing all logs.")
        
        if not user_id:
            # Confirm before clearing all
            confirm = await ctx.send(
                f"{E('warning')} **WARNING:** This will clear ALL bot logs.\n"
                f"Reply with `yes` to confirm."
            )
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "yes"
            
            try:
                import asyncio
                await bot.wait_for("message", check=check, timeout=30.0)
            except:
                return await confirm.edit(content=f"{E('error')} Clear cancelled (timeout).")
            
            loading = await ctx.send(f"{E('loading')} Clearing all logs...")
            cleared = _clear_all_logs()
            return await loading.edit(content=f"{E('success')} Cleared {cleared} log files.")
        
        # Clear user-specific logs
        loading = await ctx.send(f"{E('loading')} Clearing logs for `{user_id}`...")
        removed = _clear_user_logs(user_id)
        
        if removed == 0:
            return await loading.edit(content=f"{E('info')} No logs found for `{user_id}`.")
        
        await loading.edit(content=f"{E('success')} Removed {removed} log entries for `{user_id}`.")