# Python 3.13 — Clean embed factory for Rei-kun
# All admin, security, and system messages use these for consistent styling
import discord
from utils.bot_emojis import E

# Rei-kun brand colors
COLOR_MAIN    = 0xff4da6   # pink-purple (main)
COLOR_SUCCESS = 0x2ecc71   # green
COLOR_ERROR   = 0xe74c3c   # red
COLOR_WARN    = 0xf39c12   # orange
COLOR_INFO    = 0x9b59b6   # purple
COLOR_DARK    = 0x2f3136   # dark embed


def _base(title: str, desc: str, color: int) -> discord.Embed:
    embed = discord.Embed(title=title, description=desc, color=color)
    return embed


# ── ToS ────────────────────────────────────────────────────────────────
def tos_embed(user: discord.abc.User) -> discord.Embed:
    embed = discord.Embed(
        title=f"{E('admin')} Rei-kun — Terms of Use",
        color=COLOR_INFO,
    )
    embed.description = (
        f"Hey {user.mention}! Before you use Rei-kun, please read and agree to the following:\n\n"
        f"> {E('star')} Don't abuse, spam, or exploit bot features\n"
        f"> {E('star')} Don't use the bot to harass or harm others\n"
        f"> {E('star')} Misuse may result in a **permanent block**\n"
        f"> {E('star')} Follow Discord's Terms of Service at all times\n\n"
        f"React **👍** to agree and continue {E('flower')}\n"
        f"React **👎** to decline"
    )
    embed.set_footer(text="Rei-kun Security System")
    return embed


def tos_agreed_embed(user: discord.abc.User) -> discord.Embed:
    embed = discord.Embed(
        title=f"{E('success')} Terms Accepted",
        description=f"Welcome, {user.mention}! {E('flower')}\nYou're all set to use Rei-kun.",
        color=COLOR_SUCCESS,
    )
    embed.set_footer(text="Rei-kun Security System")
    return embed


def tos_declined_embed(user: discord.abc.User, remaining: int) -> discord.Embed:
    if remaining <= 0:
        embed = discord.Embed(
            title=f"{E('error')} Blocked",
            description=(
                f"{user.mention} you've declined too many times.\n"
                f"You have been **blocked** from using Rei-kun."
            ),
            color=COLOR_ERROR,
        )
    else:
        embed = discord.Embed(
            title=f"{E('warning')} Terms Declined",
            description=(
                f"{user.mention} you declined the Terms of Use.\n"
                f"**{remaining}** attempt(s) remaining before auto-block."
            ),
            color=COLOR_WARN,
        )
    embed.set_footer(text="Rei-kun Security System")
    return embed


def tos_timeout_embed(user: discord.abc.User) -> discord.Embed:
    embed = discord.Embed(
        title=f"{E('warning')} Agreement Timed Out",
        description=(
            f"{user.mention} you didn't respond in time.\n"
            f"Use any command again to see the Terms of Use."
        ),
        color=COLOR_WARN,
    )
    embed.set_footer(text="Rei-kun Security System")
    return embed


# ── Admin actions ──────────────────────────────────────────────────────
def admin_action_embed(action: str, actor: discord.abc.User,
                       target: discord.abc.User, color: int = COLOR_INFO) -> discord.Embed:
    embed = discord.Embed(title=f"{E('admin')} {action}", color=color)
    embed.add_field(name="Target",    value=target.mention, inline=True)
    embed.add_field(name="Action by", value=actor.mention,  inline=True)
    embed.set_footer(text=f"Rei-kun Admin System {E('crown')}")
    return embed


# ── Generic ────────────────────────────────────────────────────────────
def success(title: str, desc: str = "") -> discord.Embed:
    return _base(f"{E('success')} {title}", desc, COLOR_SUCCESS)

def error(title: str, desc: str = "") -> discord.Embed:
    return _base(f"{E('error')} {title}", desc, COLOR_ERROR)

def warn(title: str, desc: str = "") -> discord.Embed:
    return _base(f"{E('warning')} {title}", desc, COLOR_WARN)

def info(title: str, desc: str = "") -> discord.Embed:
    return _base(f"{E('info')} {title}", desc, COLOR_INFO)
