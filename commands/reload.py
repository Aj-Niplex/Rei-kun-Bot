# Python 3.13 | discord.py 2.6.4
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Iterable

import discord
from discord.ext import commands

from utils.config_loader import BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS
from utils.bot_emojis import E

FOOTER = "Rei-kun Reload System v6.2"

DEPENDENCY_RELOADS: dict[str, list[str]] = {
    "utils.ai": ["commands.ai"],
    "utils.concurrency": ["commands.ai"],
    "utils.conversation": ["commands.ai"],
    "utils.emoji_assets": ["commands.ai"],
}

ALIASES: dict[str, list[str]] = {
    "ai": ["utils.ai", "commands.ai"],
    "logs": ["commands.logs"],
    "reload": ["commands.reload"],
    "doctor": ["commands.doctor"],
}


def _is_admin(u: discord.abc.User) -> bool:
    return (
        str(u.id) in BOT_ADMIN_USER_IDS
        or str(getattr(u, "name", "")).lower() in {x.lower() for x in BOT_ADMIN_USERS}
    )


def _all_modules() -> list[str]:
    mods: list[str] = []
    for d in ("commands", "utils"):
        p = Path(d)
        if not p.exists():
            continue
        for f in sorted(p.iterdir()):
            if f.suffix == ".py" and f.name != "__init__.py":
                mods.append(f"{d}.{f.stem}")
    return mods


def _normalize_request(raw: str) -> str:
    raw = raw.strip().replace("\\", "/")
    raw = raw.replace("/", ".")
    if raw.endswith(".py"):
        raw = raw[:-3]
    return raw


def _expand_targets(request: str) -> list[str]:
    req = _normalize_request(request).lower()

    if req == "all":
        return _all_modules()

    if req in ("commands", "utils"):
        return [m for m in _all_modules() if m.startswith(req + ".")]

    if req in ALIASES:
        return ALIASES[req][:]

    if req.startswith("commands.") or req.startswith("utils."):
        return [req]

    return [req]


def _add_dependencies(targets: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()

    def add(mod: str) -> None:
        if mod not in seen:
            seen.add(mod)
            out.append(mod)

    for mod in targets:
        add(mod)
        for dep in DEPENDENCY_RELOADS.get(mod, []):
            add(dep)

    return out


async def _reload_one(bot: commands.Bot, mod: str) -> tuple[bool, str]:
    try:
        importlib.invalidate_caches()

        # Only use extension system for actual command files, not utils
        if mod.startswith("commands.") and "." not in mod[9:]:  # e.g. "commands.ai" not "commands.utils.X"
            try:
                await bot.reload_extension(mod)
            except commands.ExtensionNotLoaded:
                await bot.load_extension(mod)
        else:
            # For utils modules, slash_commands, or anything else, use importlib
            if mod in sys.modules:
                importlib.reload(sys.modules[mod])
            else:
                importlib.import_module(mod)

        return True, ""
    except Exception as e:
        return False, str(e)


async def setup(bot: commands.Bot) -> None:
    bot.remove_command("reload")

    @bot.command(name="reload")
    async def reload_cmd(ctx: commands.Context, *, module: str = "all") -> None:
        if not _is_admin(ctx.author):
            return await ctx.send(f"{E('error')} Admin only.")

        raw_targets = _expand_targets(module)
        targets = _add_dependencies(raw_targets)

        # Animated loading message
        start = discord.Embed(
            title=f"{E('loading')} Reloading Modules...",
            description=f"**Target:** `{module}`\n{E('sparkle')} Invalidating caches...",
            color=0xF39C12,
        )
        start.set_footer(text=f"{FOOTER} {E('ribbon')}")
        msg = await ctx.send(embed=start)

        success: list[tuple[str, str]] = []
        failed: list[tuple[str, str]] = []

        # Show progress animation for each module
        for i, mod in enumerate(targets):
            progress_embed = discord.Embed(
                title=f"{E('loading')} Reloading... ({i+1}/{len(targets)})",
                description=f"**Current:** `{mod}`",
                color=0xF39C12,
            )
            progress_embed.set_footer(text=f"{FOOTER} {E('ribbon')}")
            await msg.edit(embed=progress_embed)
            
            ok, err = await _reload_one(bot, mod)
            (success if ok else failed).append((mod, err))

        color = 0x2ECC71 if not failed else (0xE74C3C if not success else 0xF39C12)
        embed = discord.Embed(color=color)

        if module.strip().lower() == "all":
            embed.title = f"{E('reload')} Reload All Complete"
            embed.add_field(name=f"{E('success')} Reloaded", value=str(len(success)), inline=True)
            embed.add_field(name=f"{E('error')} Failed", value=str(len(failed)), inline=True)
            if success:
                embed.add_field(
                    name=f"{E('sparkle')} SUCCESS:",
                    value="\n".join(f"• {m}" for m, _ in success)[:1020],
                    inline=False,
                )
        elif failed:
            embed.title = f"{E('error')} Reload Failed"
        else:
            embed.title = f"{E('reload')} Reload Complete"
            embed.add_field(name=f"{E('success')} Done", value=f"`{success[0][0]}`", inline=False)

        if failed:
            embed.add_field(
                name=f"{E('warning')} FAILURES:",
                value="\n".join(f"**{m}**\n  {e}" for m, e in failed)[:1020],
                inline=False,
            )

        embed.set_footer(text=f"{FOOTER} {E('ribbon')}")
        await msg.edit(embed=embed)
