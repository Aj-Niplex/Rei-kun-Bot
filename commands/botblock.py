import discord
from discord.ext import commands
from utils.config_loader import BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS
from utils.storage import block_user
from utils.vps_logger import log_action, log_error, log_success
from utils import embeds as emb

def _is_admin(ctx: commands.Context) -> bool:
    return (str(ctx.author.id) in BOT_ADMIN_USER_IDS
            or str(getattr(ctx.author,"name","")).lower() in {x.lower() for x in BOT_ADMIN_USERS})

async def setup(bot: commands.Bot) -> None:
    bot.remove_command("botblock")

    @bot.command(name="botblock")
    async def botblock(ctx: commands.Context, member: discord.Member) -> None:
        if not _is_admin(ctx):
            log_error("BOTBLOCK_DENIED", f"actor={ctx.author}")
            return await ctx.reply(embed=emb.error("No Permission"), mention_author=False)
        block_user(member.id)
        log_action("BOTBLOCK", ctx.author, f"target={member.id}")
        log_success("BOTBLOCK_DONE", f"target={member.id}")
        await ctx.send(embed=emb.admin_action_embed("User Blocked", ctx.author, member, emb.COLOR_ERROR))
