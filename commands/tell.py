from discord.ext import commands
from utils.ai import ask_ai
from utils.animations import AIAnimation
from utils.bot_emojis import E


async def setup(bot: commands.Bot) -> None:
    bot.remove_command("tell")
    bot.remove_command("tr")

    @bot.command(name="tell", aliases=["tr"])
    async def tell(ctx: commands.Context) -> None:
        if not ctx.message.reference:
            return await ctx.reply(f"{E('error')} Reply to a message first.", mention_author=False)
        ref = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        prompt = f"Translate and explain this message simply:\n\n{ref.content}"
        anim = AIAnimation(bot, ctx)
        await anim.start()
        try:
            result = await ask_ai(prompt, guild_id=(ctx.guild.id if ctx.guild else "dm"), channel_id=ctx.channel.id, author_name=str(ctx.author.display_name))
            await anim.finish(result)
        except Exception as e:
            await anim.error(f"{E('error')} Error: `{e}`")
