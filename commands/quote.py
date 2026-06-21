from discord.ext import commands
from utils.ai import ask_ai
from utils.animations import AIAnimation
from utils.bot_emojis import E


async def setup(bot: commands.Bot) -> None:
    bot.remove_command("quote")

    @bot.command()
    async def quote(ctx: commands.Context) -> None:
        anim = AIAnimation(bot, ctx)
        await anim.start()
        try:
            result = await ask_ai("Write one beautiful short motivational quote under 15 words. Just the quote, no extra text.", guild_id=(ctx.guild.id if ctx.guild else "dm"))
            await anim.finish(f"{E('ribbon')} *{result.strip()}*")
        except Exception as e:
            await anim.error(f"{E('error')} Error: `{e}`")
