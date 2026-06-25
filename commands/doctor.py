from __future__ import annotations

import ast
from pathlib import Path

import discord
from discord.ext import commands

from utils.config_loader import BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS
from utils.bot_emojis import E
from utils.code_doctor import build_report, make_backup, read_source, rollback_file, resolve_target, reload_related

FOOTER = "Reload Doctor v6.0"


def _is_admin(u: discord.abc.User) -> bool:
    return (
        str(u.id) in BOT_ADMIN_USER_IDS
        or str(getattr(u, "name", "")).lower() in {x.lower() for x in BOT_ADMIN_USERS}
    )


def _parse_flags(raw: str) -> tuple[str, set[str]]:
    parts = raw.split()
    flags = {p for p in parts if p.startswith("--")}
    query = " ".join(p for p in parts if not p.startswith("--")).strip()
    return query, flags


async def setup(bot: commands.Bot) -> None:
    @bot.command(name="doctor")
    async def doctor_cmd(ctx: commands.Context, *, target: str = "") -> None:
        if not _is_admin(ctx.author):
            return await ctx.send(f"{E('error')} Admin only.")

        query, flags = _parse_flags(target)

        if "--rollback" in flags:
            if not query:
                return await ctx.send(f"{E('warning')} Usage: `?doctor <file> --rollback`")
            path = resolve_target(query) or Path(query)
            if not path.exists():
                return await ctx.send(f"{E('error')} File not found: `{query}`")
            try:
                backup = rollback_file(path)
                return await ctx.send(f"{E('success')} Rollback done from `{backup.name}`.")
            except Exception as e:
                return await ctx.send(f"{E('error')} Rollback failed: `{e}`")

        path = None
        source = ""
        filename = "unknown.py"

        if query:
            path = resolve_target(query) or Path(query)
            if path.exists():
                source = read_source(path)
                filename = path.as_posix()
            else:
                return await ctx.send(f"{E('error')} File not found: `{query}`")

        if not source and ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            raw = await attachment.read()
            try:
                source = raw.decode("utf-8")
            except Exception:
                source = raw.decode("utf-8", errors="ignore")
            filename = attachment.filename

        if not source:
            return await ctx.send(f"{E('warning')} Usage: `?doctor <filename>` or attach a `.py` file.")

        # Show loading animation while analyzing
        loading_msg = await ctx.send(f"{E('loading')} Analyzing code... Running diagnostics...")

        report, findings, patch_plan = build_report(source, filename, note=" ".join(sorted(flags)) if flags else "")
        
        await loading_msg.delete()

        try:
            dm = await ctx.author.create_dm()
            if len(report) > 2000:
                for i in range(0, len(report), 2000):
                    await dm.send(report[i:i+2000])
            else:
                await dm.send("```\n" + report + "\n```")
            await ctx.send(f"{E('info')} Full report sent to your DMs.")
        except Exception:
            if len(report) <= 1900:
                await ctx.send("```\n" + report + "\n```")
            else:
                await ctx.send("```\n" + report[:1900] + "\n... (truncated)```")

        if patch_plan.changes > 0 and path and path.exists():
            view = ApplyPatchView(
                bot=bot,
                owner_id=ctx.author.id,
                path=path,
                patched_source=patch_plan.patched_source,
            )
            await ctx.send(f"**{patch_plan.changes} auto-fix(es) available.** Apply them?", view=view)
        elif path:
            await ctx.send(f"{E('info')} No safe auto-patches found. Manual edit needed.")


class ApplyPatchView(discord.ui.View):
    def __init__(self, *, bot: commands.Bot, owner_id: int, path: Path, patched_source: str):
        super().__init__(timeout=180)
        self.bot = bot
        self.owner_id = owner_id
        self.path = path
        self.patched_source = patched_source
        self.done = False

    def _allowed(self, interaction: discord.Interaction) -> bool:
        return _is_admin(interaction.user) and interaction.user.id == self.owner_id

    @discord.ui.button(label="Apply Fix", style=discord.ButtonStyle.success, emoji="✅")
    async def apply_fix(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self._allowed(interaction):
            return await interaction.response.send_message("Admin only.", ephemeral=True)
        if self.done:
            return await interaction.response.send_message("Already handled.", ephemeral=True)

        try:
            backup = make_backup(self.path)
            self.path.write_text(self.patched_source, encoding="utf-8")
            self.done = True
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(content=f"✅ Applied. Backup saved as `{backup.name}`.", view=self)
        except Exception as e:
            await interaction.response.send_message(f"Apply failed: `{e}`", ephemeral=True)

    @discord.ui.button(label="Apply & Reload", style=discord.ButtonStyle.primary, emoji="🔄")
    async def apply_reload(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self._allowed(interaction):
            return await interaction.response.send_message("Admin only.", ephemeral=True)
        if self.done:
            return await interaction.response.send_message("Already handled.", ephemeral=True)

        try:
            backup = make_backup(self.path)
            self.path.write_text(self.patched_source, encoding="utf-8")

            try:
                ast.parse(self.patched_source)
            except SyntaxError as e:
                return await interaction.response.send_message(f"Syntax still broken: `{e}`", ephemeral=True)

            mod = None
            # try to reload related modules based on file path
            from utils.code_doctor import path_to_module
            mod = path_to_module(self.path)

            reload_result = []
            if mod:
                reload_result = await reload_related(self.bot, mod)

            self.done = True
            for item in self.children:
                item.disabled = True

            if reload_result:
                failed = [f"{m}: {e}" for m, ok, e in reload_result if not ok]
                if failed:
                    content = f"Applied. Backup: `{backup.name}`\nReload issues:\n```text\n" + "\n".join(failed[:8]) + "\n```"
                else:
                    content = f"✅ Applied and reloaded. Backup: `{backup.name}`"
            else:
                content = f"✅ Applied. Backup saved as `{backup.name}`. Reload module manually."

            await interaction.response.edit_message(content=content, view=self)
        except Exception as e:
            await interaction.response.send_message(f"Apply+Reload failed: `{e}`", ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, emoji="❌")
    async def reject_fix(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self._allowed(interaction):
            return await interaction.response.send_message("Admin only.", ephemeral=True)
        if self.done:
            return await interaction.response.send_message("Already handled.", ephemeral=True)

        self.done = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="Rejected. No changes were made.", view=self)
