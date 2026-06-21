from discord.ext import commands
from pathlib import Path
from utils.config_loader import BOT_ADMIN_USERS
from utils.bot_emojis import E

PROMPT_FILE = Path("ai/system prompt.txt")

def is_admin(user):
    return str(user.name).lower() in {x.lower() for x in BOT_ADMIN_USERS}

async def setup(bot):
    # Remove existing commands before re-registering (fixes reload)
    bot.remove_command("setprompt")

    @bot.command()
    async def setprompt(ctx, *, text=None):
        if not is_admin(ctx.author): return
        if ctx.guild is not None:
            return await ctx.reply(f"{E('error')} DM only.", mention_author=False)
        if not text:
            return await ctx.reply(f"{E('info')} Usage: `?setprompt <new text>`", mention_author=False)
        PROMPT_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROMPT_FILE.write_text(text, encoding="utf-8")
        await ctx.reply(f"{E('success')} System prompt updated.", mention_author=False)
