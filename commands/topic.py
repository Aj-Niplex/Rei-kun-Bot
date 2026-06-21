from discord.ext import commands
from utils.ai import ask_ai
from utils.animations import AIAnimation
from utils.bot_emojis import E


async def setup(bot: commands.Bot) -> None:
    bot.remove_command("topic")

    @bot.command()
    async def topic(ctx: commands.Context) -> None:
        anim = AIAnimation(bot, ctx)
        await anim.start()
        try:
            result = await ask_ai("Generate one fun or emotional conversation starter topic. Keep it short.", guild_id=(ctx.guild.id if ctx.guild else "dm"))
            await anim.finish(f"{E('sparkle')} {result.strip()}")
        except Exception as e:
            await anim.error(f"{E('error')} Error: `{e}`")
