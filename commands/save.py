from discord.ext import commands
from utils.storage import save_memory
from utils.bot_emojis import E

async def setup(bot):
    # Remove existing commands before re-registering (fixes reload)
    bot.remove_command("save")

    @bot.command()
    async def save(ctx):
        if not ctx.message.reference:
            return await ctx.reply(f"{E('error')} Reply to a message first.", mention_author=False)
        replied = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        content = (replied.content or "").lower()
        category = "memories"
        if "promise" in content:                                          category = "promises"
        elif "fight" in content or "argument" in content:                category = "fights"
        elif any(x in content for x in ["birthday","anniversary","date"]): category = "dates"
        guild_id = ctx.guild.id if ctx.guild else "dm"
        save_memory(guild_id, category, replied.content or "")
        await ctx.send(f"{E('memory')} Saved to **{category}** {E('sparkle')}")
