# Python 3.13 | discord.py 2.6.4
import asyncio
import discord
from discord.ext import commands
from utils.config_loader import BOT_DEV, BOT_VERSION
from utils.bot_emojis import E


async def _bar(msg: discord.Message, title: str) -> None:
    bars = ["░░░░░░░░░░ 0%","██░░░░░░░░ 20%","████░░░░░░ 40%",
            "██████░░░░ 60%","████████░░ 80%","██████████ 100%"]
    for b in bars:
        await msg.edit(content=f"{title}\n```{b}```")
        await asyncio.sleep(0.12)


async def setup(bot: commands.Bot) -> None:
    bot.remove_command("botinfo")
    bot.remove_command("aboutbot")

    @bot.command(name="botinfo", aliases=["aboutbot"])
    async def botinfo(ctx: commands.Context) -> None:
        msg = await ctx.send(f"{E('loading')} Rei-kun System Initializing...")
        await _bar(msg, f"{E('info')} Searching Developer Database")
        await msg.edit(content=f"{E('success')} Developer Found")
        await asyncio.sleep(0.2)
        await _bar(msg, f"{E('loading')} Collecting Bot Information")
        await msg.edit(content=f"{E('success')} Information Collected")
        await asyncio.sleep(0.2)
        await _bar(msg, f"{E('sparkle')} Sending Information")

        embed = discord.Embed(
            title=f"{E('crown')} Rei-kun",
            description=(
                f"{E('flower')} Advanced AI Discord Utility Bot\n"
                "Built for AI, Automation, Memory, Admin and VPS Deployment."
            ),
            color=0xff4da6,
        )
        embed.add_field(name=f"{E('dev')} Developer",  value=f"```{BOT_DEV}```",     inline=False)
        embed.add_field(name=f"{E('star')} Version",   value=f"```{BOT_VERSION}```", inline=True)
        embed.add_field(
            name=f"{E('sparkle')} AI",
            value=(
                f"{E('sparkle')} Multi-Model\n"
                f"{E('sparkle')} Auto Fallback\n"
                f"{E('sparkle')} Translation\n"
                f"{E('sparkle')} Smart Replies"
            ),
            inline=False,
        )
        embed.add_field(
            name=f"{E('memory')} Memory",
            value=(
                f"{E('paws')} Server Memory\n"
                f"{E('paws')} Saved Notes\n"
                f"{E('paws')} Context Recall"
            ),
            inline=True,
        )
        embed.add_field(
            name=f"{E('admin')} Admin",
            value=(
                f"{E('crown')} Reload\n"
                f"{E('crown')} Blocking\n"
                f"{E('crown')} Promotions"
            ),
            inline=True,
        )
        embed.add_field(
            name=f"{E('flower')} Extras",
            value=(
                f"{E('butterfly')} Custom Emojis\n"
                f"{E('butterfly')} Help System\n"
                f"{E('butterfly')} Logs"
            ),
            inline=True,
        )
        embed.add_field(
            name=f"{E('info')} Runtime",
            value=(
                f"Guilds: `{len(bot.guilds)}`\n"
                f"Users: `{sum(g.member_count for g in bot.guilds if g.member_count)}`"
            ),
            inline=False,
        )
        embed.set_footer(text=f"Rei-kun {E('flower')} {BOT_VERSION}")
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        await msg.edit(content="", embed=embed)
