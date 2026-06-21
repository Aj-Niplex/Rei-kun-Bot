from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable

import discord
from discord.ext import commands

try:
    from utils.bot_emojis import E
except Exception:
    def E(name: str) -> str:
        fallback = {
            "crown": "👑",
            "flower": "🌸",
        }
        return fallback.get(name, "✨")


HELP_COLOR = 0xFF4DA6
MENU_TIMEOUT = 90

OVERVIEW_EMOJI = "🏠"
BASIC_EMOJI = "1️⃣"
ADVANCED_EMOJI = "2️⃣"
RANDOM_EMOJI = "3️⃣"
ADMIN_EMOJI = "4️⃣"
OWNER_EMOJI = "5️⃣"
BACK_EMOJI = "🔙"
CLOSE_EMOJI = "❌"

REACTION_ORDER = [
    OVERVIEW_EMOJI,
    BASIC_EMOJI,
    ADVANCED_EMOJI,
    RANDOM_EMOJI,
    ADMIN_EMOJI,
    OWNER_EMOJI,
    BACK_EMOJI,
    CLOSE_EMOJI,
]


@dataclass(frozen=True)
class HelpCategory:
    title: str
    subtitle: str
    commands: tuple[tuple[str, str], ...]


CATEGORIES: dict[str, HelpCategory] = {
    OVERVIEW_EMOJI: HelpCategory(
        title="Bot Overview",
        subtitle="Main info, features and quick starting points",
        commands=(
            ("!help or ?help", "Open this help menu"),
            ("!botinfo", "Show bot version, developer and features"),
            ("!ping", "Show latency, CPU and RAM"),
            ("!ai <question>", "Ask AI to explain, translate, summarize or chat"),
            ("!resource <code>", "Get a study resource by code"),
        ),
    ),
    BASIC_EMOJI: HelpCategory(
        title="Basic & OG Commands",
        subtitle="Most used commands for normal chat and simple actions",
        commands=(
            ("!help or ?help", "Open the command menu"),
            ("!ai <question>", "Ask AI to explain, translate, summarize or chat"),
            ("!aihelp", "Show AI usage examples and tips"),
            ("!clearhistory", "Reset AI conversation memory for this channel"),
            ("!ping", "Show bot latency, CPU and RAM"),
            ("!quote", "Get a random inspirational quote"),
            ("!topic", "Get a conversation starter"),
            ("!userid <@user>", "Find a member's user ID"),
            ("!botinfo", "Show version, owner and purpose"),
        ),
    ),
    ADVANCED_EMOJI: HelpCategory(
        title="Advanced Commands",
        subtitle="Power tools, automation and deeper bot controls",
        commands=(
            ("!fix", "Rewrite a replied message softly"),
            ("!prompt", "Show current prompt path"),
            ("!setprompt", "Upload a new prompt file"),
            ("!emojisync", "Sync app emojis from Discord"),
            ("!emoji list", "Browse available custom emojis"),
            ("!resourceadd", "Add a new study resource"),
            ("!resourceedit", "Edit an existing resource"),
            ("!backup", "Create a backup of the bot"),
            ("!save", "Save a replied message to memory"),
            ("!remember", "Show saved memory for this server"),
        ),
    ),
    RANDOM_EMOJI: HelpCategory(
        title="Random / Fun Commands",
        subtitle="Small useful extras and casual commands",
        commands=(
            ("!quote", "Get a random inspirational quote"),
            ("!topic", "Get a fun conversation starter"),
            ("!tell", "Explain or translate a replied message"),
            ("!activity", "Show bot stats and activity"),
        ),
    ),
    ADMIN_EMOJI: HelpCategory(
        title="Admin Only",
        subtitle="Commands that need admin or moderator access",
        commands=(
            ("!botblock <user_id>", "Block a user from the bot"),
            ("!botunblock <user_id>", "Remove a user block"),
            ("!promote <@user>", "Give a user the Admin role"),
            ("!demote <@user>", "Remove Admin role from a user"),
            ("!admins", "List users with Admin role"),
            ("!logs", "View all recent bot logs"),
            ("!logs <user_id>", "View logs for specific user"),
            ("!clearlogs <user_id>", "Clear logs for specific user"),
            ("!doctor <file>", "Check code health and suggest fixes"),
            ("!reload <module>", "Reload a command or utility module"),
        ),
    ),
    OWNER_EMOJI: HelpCategory(
        title="Owner / Dev Only",
        subtitle="Maintenance tools for the bot owner or trusted devs",
        commands=(
            ("!reload all", "Reload every command and utility"),
            ("!doctor <file>", "Inspect code and apply fixes"),
            ("!setprompt", "Upload new system prompt"),
            ("!vpslogs or !vlog", "View VPS system logs"),
            ("!clearlogs", "Clear all bot logs (confirmation)"),
        ),
    ),
}


def _safe_title(text: str) -> str:
    return text.replace("_", " ").strip()


def _build_overview_embed(bot: commands.Bot) -> discord.Embed:
    bot_name = getattr(bot.user, "name", "Rei-kun")
    description = (
        f"{E('crown')} **Rei-kun Help Menu**\n\n"
        "Use the reactions below to open the command group you want.\n"
        "This menu is made for quick browsing, so you do not need to remember every command.\n\n"
        "**Main features**\n"
        "• AI chat and reply tools\n"
        "• Memory and saving tools\n"
        "• Study resource hub\n"
        "• Emoji sync and emoji tools\n"
        "• Doctor, reload and fix tools\n"
        "• Admin and owner controls\n\n"
        "**How to use**\n"
        "• Tap the reaction that matches the category\n"
        "• Tap ❌ to close the menu\n"
        "• Run /help again anytime to reopen it"
    )

    embed = discord.Embed(
        title=f"{E('crown')} {bot_name} · Help",
        description=description,
        color=HELP_COLOR,
    )
    embed.add_field(
        name="Quick info",
        value=(
            f"**Bot:** {bot_name}\n"
            f"**Style:** Slash + prefix support\n"
            f"**Menu:** Reaction based category chooser"
        ),
        inline=False,
    )
    embed.add_field(
        name="Category map",
        value=(
            f"{OVERVIEW_EMOJI} Overview\n"
            f"{BASIC_EMOJI} Basic & OG\n"
            f"{ADVANCED_EMOJI} Advanced\n"
            f"{RANDOM_EMOJI} Random / Fun\n"
            f"{ADMIN_EMOJI} Admin only\n"
            f"{OWNER_EMOJI} Owner / Dev\n"
            f"{BACK_EMOJI} Back to overview\n"
            f"{CLOSE_EMOJI} Close"
        ),
        inline=False,
    )
    embed.set_footer(text=f"Rei-kun {E('flower')} · Use !help or ?help")
    return embed


def _build_category_embed(category: HelpCategory) -> discord.Embed:
    lines = [f"`{cmd}` — {desc}" for cmd, desc in category.commands]
    text = "\n".join(lines) if lines else "No commands found in this group yet."

    embed = discord.Embed(
        title=f"{E('crown')} {category.title}",
        description=f"**{category.subtitle}**\n\n{text}",
        color=HELP_COLOR,
    )
    embed.set_footer(text=f"Rei-kun {E('flower')} · Tap another reaction to switch category")
    return embed


async def _safe_add_reaction(message: discord.Message, emoji: str) -> None:
    try:
        await message.add_reaction(emoji)
    except discord.HTTPException:
        pass
    except discord.Forbidden:
        pass


async def _safe_clear_reactions(message: discord.Message) -> None:
    try:
        await message.clear_reactions()
    except discord.HTTPException:
        pass
    except discord.Forbidden:
        pass


async def _render_menu(bot: commands.Bot, message: discord.Message, author_id: int) -> None:
    for emoji in REACTION_ORDER:
        await _safe_add_reaction(message, emoji)

    def check(reaction: discord.Reaction, user: discord.User | discord.Member) -> bool:
        return (
            user.id == author_id
            and reaction.message.id == message.id
            and str(reaction.emoji) in (list(CATEGORIES.keys()) + [CLOSE_EMOJI, BACK_EMOJI])
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=MENU_TIMEOUT, check=check)
        except asyncio.TimeoutError:
            await _safe_clear_reactions(message)
            return

        emoji = str(reaction.emoji)
        if emoji == CLOSE_EMOJI:
            await _safe_clear_reactions(message)
            try:
                await message.edit(content="Help menu closed.", embed=None)
            except discord.HTTPException:
                pass
            return

        if emoji == BACK_EMOJI:
            try:
                await message.edit(embed=_build_overview_embed(bot), content=None)
            except discord.HTTPException:
                pass
            try:
                await message.remove_reaction(reaction.emoji, user)
            except discord.HTTPException:
                pass
            except discord.Forbidden:
                pass
            continue

        category = CATEGORIES.get(emoji)
        if category is None:
            continue

        try:
            await message.edit(embed=_build_category_embed(category), content=None)
        except discord.HTTPException:
            continue

        try:
            await message.remove_reaction(reaction.emoji, user)
        except discord.HTTPException:
            pass
        except discord.Forbidden:
            pass


async def _send_prefix_help(ctx: commands.Context) -> None:
    message = await ctx.send(embed=_build_overview_embed(ctx.bot))
    await _render_menu(ctx.bot, message, ctx.author.id)


async def _send_slash_help(interaction: discord.Interaction, bot: commands.Bot) -> None:
    await interaction.response.send_message(embed=_build_overview_embed(bot))
    message = await interaction.original_response()
    await _render_menu(bot, message, interaction.user.id)


async def setup(bot: commands.Bot) -> None:
    bot.remove_command("help")
    bot.remove_command("helpme")

    @bot.hybrid_command(name="help", aliases=["helpme"], description="Show the help menu")
    async def help_cmd(ctx: commands.Context) -> None:
        if ctx.interaction is not None:
            await _send_slash_help(ctx.interaction, ctx.bot)
            return
        await _send_prefix_help(ctx)
