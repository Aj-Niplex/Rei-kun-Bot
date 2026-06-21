# Python 3.13 — AI waiting animation system
import asyncio
import random
import discord

FRAMES: list[str] = [
    "🔍  Scanning knowledge base...",
    "🧠  Processing your request...",
    "⚡  Connecting to AI models...",
    "📡  Fetching response...",
    "🔮  Reading the void...",
    "✨  Generating answer...",
    "🌀  Thinking deeply...",
    "💭  Consulting the matrix...",
    "🎯  Analyzing context...",
    "🛰️  Reaching out to servers...",
    "🧬  Structuring reply...",
    "🌌  Searching across dimensions...",
    "📚  Checking knowledge logs...",
    "🤖  Neural nets firing...",
    "🎲  Crunching tokens...",
]

class AIAnimation:
    """
    Cycles random loading messages while AI is thinking.
    Call start() → AI runs → call finish(content) to send result.
    """

    def __init__(self, bot: discord.Client, ctx):
        self.bot   = bot
        self.ctx   = ctx
        self.msg: discord.Message | None = None
        self._task: asyncio.Task | None  = None
        self._done = False

    async def start(self) -> None:
        first = random.choice(FRAMES)
        self.msg = await self.ctx.reply(first, mention_author=False)
        self._task = asyncio.create_task(self._cycle())

    async def _cycle(self) -> None:
        pool = FRAMES.copy()
        idx  = 0
        try:
            while not self._done:
                await asyncio.sleep(1.8)
                if self._done:
                    break
                frame = pool[idx % len(pool)]
                idx  += 1
                try:
                    await self.msg.edit(content=frame)
                except Exception:
                    break
        except asyncio.CancelledError:
            pass

    async def finish(self, content: str) -> discord.Message | None:
        """Stop animation → flash 'Sending...' → deliver result."""
        self._done = True
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        # Flash "Sending..." for 0.2s so it feels snappy
        try:
            await self.msg.edit(content="📤  Sending...")
            await asyncio.sleep(0.2)
        except Exception:
            pass

        # Discord has a 2000-char limit per message
        if len(content) <= 1900:
            try:
                await self.msg.edit(content=content)
                return self.msg
            except Exception:
                pass

        # Long response — delete animation msg, send as new message
        try:
            await self.msg.delete()
        except Exception:
            pass

        # Split into chunks
        chunks = [content[i:i+1900] for i in range(0, len(content), 1900)]
        last = None
        for chunk in chunks:
            last = await self.ctx.channel.send(chunk)
        return last

    async def error(self, content: str) -> None:
        """Show error, cancel animation."""
        self._done = True
        if self._task and not self._task.done():
            self._task.cancel()
        try:
            await self.msg.edit(content=content)
        except Exception:
            await self.ctx.channel.send(content)
