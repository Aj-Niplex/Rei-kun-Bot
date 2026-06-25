# Python 3.13 | discord.py 2.6.4
import discord
from discord.ext import commands
from utils.config_loader import BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS, BOT_OWNER_USER_IDS
from utils.vps_logger import log_error, log_success
from utils.bot_emojis import E
from utils import embeds as emb


class AdminPromotion(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _can_act(self, user: discord.abc.User) -> bool:
        if isinstance(user, discord.Member) and user.guild_permissions.administrator:
            return True
        uid  = str(user.id)
        name = str(getattr(user, "name", "")).lower()
        return (uid in BOT_OWNER_USER_IDS or uid in BOT_ADMIN_USER_IDS
                or name in {x.lower() for x in BOT_ADMIN_USERS})

    @commands.command(name="promote")
    async def promote(self, ctx: commands.Context, member: discord.Member) -> None:
        if not self._can_act(ctx.author):
            log_error("PROMOTE_DENIED", f"actor={ctx.author} target={member}")
            return await ctx.reply(embed=emb.error("No Permission", "You cannot promote users."), mention_author=False)

        role = discord.utils.get(ctx.guild.roles, name="Admin") or await ctx.guild.create_role(name="Admin", reason=f"By {ctx.author}")
        try:
            await member.add_roles(role, reason=f"Promoted by {ctx.author}")
            await ctx.reply(embed=emb.admin_action_embed("Admin Promotion", ctx.author, member, emb.COLOR_SUCCESS), mention_author=False)
            log_success("PROMOTION_DONE", f"{member} -> Admin")
        except Exception as e:
            await ctx.reply(embed=emb.error("Promotion Failed", f"`{e}`"), mention_author=False)
            log_error("PROMOTION_FAILED", str(e))

    @commands.command(name="demote")
    async def demote(self, ctx: commands.Context, member: discord.Member) -> None:
        if not self._can_act(ctx.author):
            log_error("DEMOTE_DENIED", f"actor={ctx.author} target={member}")
            return await ctx.reply(embed=emb.error("No Permission", "You cannot demote users."), mention_author=False)

        role = discord.utils.get(ctx.guild.roles, name="Admin")
        try:
            if role and role in member.roles:
                await member.remove_roles(role, reason=f"Demoted by {ctx.author}")
            await ctx.reply(embed=emb.admin_action_embed("Admin Demotion", ctx.author, member, emb.COLOR_WARN), mention_author=False)
            log_success("DEMOTION_DONE", str(member))
        except Exception as e:
            await ctx.reply(embed=emb.error("Demotion Failed", f"`{e}`"), mention_author=False)
            log_error("DEMOTION_FAILED", str(e))

    @commands.command(name="admins")
    async def admins(self, ctx: commands.Context) -> None:
        role = discord.utils.get(ctx.guild.roles, name="Admin")
        if not role or not role.members:
            return await ctx.reply(embed=emb.info("No Admins", "No Admin role found."), mention_author=False)
        embed = discord.Embed(
            title=f"{E('crown')} Current Admins",
            description="\n".join(m.mention for m in role.members),
            color=emb.COLOR_INFO,
        )
        embed.set_footer(text=f"Rei-kun Admin System {E('ribbon')}")
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot) -> None:
    if bot.get_cog("AdminPromotion"):
        await bot.remove_cog("AdminPromotion")
    await bot.add_cog(AdminPromotion(bot))
