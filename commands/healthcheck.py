from __future__ import annotations

import importlib
import sys
from pathlib import Path

import discord
from discord.ext import commands

from utils.config_loader import BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS
from utils.bot_emojis import E


def _is_admin(u: discord.abc.User) -> bool:
    return (
        str(u.id) in BOT_ADMIN_USER_IDS
        or str(getattr(u, "name", "")).lower() in {x.lower() for x in BOT_ADMIN_USERS}
    )


async def setup(bot: commands.Bot) -> None:
    @bot.command(name="healthcheck", aliases=["health", "status"])
    async def healthcheck_cmd(ctx: commands.Context) -> None:
        """
        Comprehensive health check of all bot systems.
        Shows which modules loaded successfully and which failed.
        """
        if not _is_admin(ctx.author):
            return await ctx.send(f"{E('error')} Admin only.")

        embed = discord.Embed(
            title="🏥 Rei-kun Health Check",
            color=discord.Color.blue(),
            description="Checking all systems...",
        )
        
        # Check utils modules
        utils_modules = [
            "utils.ai",
            "utils.animations",
            "utils.bot_emojis",
            "utils.code_doctor",
            "utils.command_catalog",
            "utils.concurrency",
            "utils.config_loader",
            "utils.conversation",
            "utils.embeds",
            "utils.emoji_assets",
            "utils.emoji_parser",
            "utils.emoji_seed",
            "utils.logger",
            "utils.message_utils",
            "utils.permissions",
            "utils.resource_store",
            "utils.storage",
            "utils.tos",
            "utils.vps_logger",
            "utils.email_sender",  # Critical: needs cryptography
        ]
        
        utils_ok = []
        utils_fail = []
        
        for mod_name in utils_modules:
            try:
                if mod_name in sys.modules:
                    # Already loaded
                    utils_ok.append(mod_name.replace("utils.", ""))
                else:
                    # Try to import
                    importlib.import_module(mod_name)
                    utils_ok.append(mod_name.replace("utils.", ""))
            except Exception as e:
                utils_fail.append(f"{mod_name.replace('utils.', '')}: {type(e).__name__}")
        
        # Check commands
        commands_path = Path("commands")
        command_files = list(commands_path.glob("*.py"))
        command_files = [f for f in command_files if f.name not in ["__init__.py", "__pycache__"]]
        
        commands_ok = []
        commands_fail = []
        
        for cmd_file in command_files:
            cmd_name = f"commands.{cmd_file.stem}"
            try:
                if cmd_name in sys.modules:
                    commands_ok.append(cmd_file.stem)
                else:
                    importlib.import_module(cmd_name)
                    commands_ok.append(cmd_file.stem)
            except Exception as e:
                commands_fail.append(f"{cmd_file.stem}: {type(e).__name__}")
        
        # Build report
        utils_text = ""
        if utils_ok:
            utils_text += f"✅ **{len(utils_ok)} utils modules OK:**\n"
            # Show first 10
            for mod in utils_ok[:10]:
                utils_text += f"├─ {mod}\n"
            if len(utils_ok) > 10:
                utils_text += f"└─ ...and {len(utils_ok) - 10} more\n"
        
        if utils_fail:
            utils_text += f"\n❌ **{len(utils_fail)} utils modules FAILED:**\n"
            for mod in utils_fail[:5]:
                utils_text += f"├─ {mod}\n"
            if len(utils_fail) > 5:
                utils_text += f"└─ ...and {len(utils_fail) - 5} more\n"
        
        commands_text = ""
        if commands_ok:
            commands_text += f"✅ **{len(commands_ok)} commands OK:**\n"
            for cmd in commands_ok[:10]:
                commands_text += f"├─ {cmd}\n"
            if len(commands_ok) > 10:
                commands_text += f"└─ ...and {len(commands_ok) - 10} more\n"
        
        if commands_fail:
            commands_text += f"\n❌ **{len(commands_fail)} commands FAILED:**\n"
            for cmd in commands_fail[:5]:
                commands_text += f"├─ {cmd}\n"
            if len(commands_fail) > 5:
                commands_text += f"└─ ...and {len(commands_fail) - 5} more\n"
        
        # Overall status
        if not utils_fail and not commands_fail:
            embed.color = discord.Color.green()
            embed.description = "🎉 **ALL SYSTEMS OPERATIONAL**"
        elif utils_fail or commands_fail:
            embed.color = discord.Color.orange()
            embed.description = "⚠️ **SOME ISSUES DETECTED**"
        
        # Add fields
        if utils_text:
            embed.add_field(
                name="📦 Utils Modules",
                value=utils_text[:1024],
                inline=False,
            )
        
        if commands_text:
            embed.add_field(
                name="⚙️ Commands",
                value=commands_text[:1024],
                inline=False,
            )
        
        # Bot stats
        stats_text = f"""
🤖 **Bot:** {bot.user.name}#{bot.user.discriminator}
🆔 **ID:** {bot.user.id}
🌐 **Servers:** {len(bot.guilds)}
👥 **Users:** {sum(g.member_count for g in bot.guilds)}
💻 **Python:** {sys.version.split()[0]}
📚 **discord.py:** {discord.__version__}
"""
        embed.add_field(
            name="📊 Bot Statistics",
            value=stats_text,
            inline=False,
        )
        
        # Quick action guide
        if utils_fail or commands_fail:
            embed.add_field(
                name="🔧 Quick Fix",
                value="Try `/reload all` to reload failed modules, or `/doctor <module_name>` to diagnose issues.",
                inline=False,
            )
        
        embed.set_footer(text="Health Check v1.0")
        
        await ctx.send(embed=embed)
