from discord.ext import commands
import discord
from utils.bot_emojis import E

async def setup(bot):
    # Remove existing commands before re-registering (fixes reload)
    bot.remove_command("aihelp")
    bot.remove_command("ahelp")

    @bot.command(name="aihelp", aliases=["ahelp"])
    async def aihelp(ctx):
        embed = discord.Embed(
            title=f"{E('gojo')} AI Help",
            color=0x9b59b6,
            description=f"Use `!ai` or `?ai` for chat, translation, explanation and more. {E('sparkle')}"
        )
        embed.add_field(
            name=f"{E('star')} Best Examples",
            value=(
                f"`!ai translate this to Hindi`\n"
                f"`!ai explain this in simple English`\n"
                f"`!ai what changed after v7.0.0?`\n"
                f"`!ai tell me the meaning of this message`\n"
                f"`?ai how do I use the logs command?`"
            ),
            inline=False,
        )
        embed.add_field(
            name=f"{E('info')} How It Works",
            value=(
                f"Reads server memory, bot help data, version logs and custom media assets. {E('memory')}\n"
                f"Keep the prompt short for faster replies."
            ),
            inline=False,
        )
        embed.add_field(
            name=f"{E('flower')} Custom Emojis",
            value=(
                f"AI uses `[[emoji_name]]` placeholders. {E('ribbon')}\n"
                f"Bot converts them to real Discord emoji tags."
            ),
            inline=False,
        )
        embed.set_footer(text=f"Rei-kun AI System {E('sparkle')}")
        await ctx.send(embed=embed)
