import discord
from discord.ext import commands
import datetime as dt
from collections import deque
from typing import Optional, Deque, Dict, List

# importa constantes do seu env novo
from utils.env import (
    FOOTER_NOME,
    FOOTER_LOGO,
    LOG_CHANNEL_ID
)

# =========================================
# Helpers gerais
# =========================================

def _fmt_dt(d: Optional[dt.datetime]) -> str:
    if not d:
        return "—"
    return d.astimezone(dt.timezone.utc).strftime("%d/%m/%Y %H:%M UTC")


def _truncate(text: Optional[str], limit: int = 1800) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _brand(embed: discord.Embed) -> discord.Embed:
    embed.set_footer(
        text=f"© {FOOTER_NOME} — Todos os direitos reservados",
        icon_url=FOOTER_LOGO or None
    )
    if FOOTER_LOGO:
        try:
            embed.set_thumbnail(url=FOOTER_LOGO)
        except Exception:
            pass
    return embed


# =========================================
# Rate limiter simples
# =========================================

class _RateLimiter:
    def __init__(self, max_events: int, window_seconds: int):
        self.max_events = max_events
        self.window = dt.timedelta(seconds=window_seconds)
        self._hits: Deque[dt.datetime] = deque()

    def allow(self) -> bool:
        now = dt.datetime.utcnow()
        while self._hits and (now - self._hits[0]) > self.window:
            self._hits.popleft()

        if len(self._hits) >= self.max_events:
            return False

        self._hits.append(now)
        return True


# =========================================
# Cog de Logs
# =========================================

class Logs(commands.Cog):
    """Logs essenciais para a cidade Vhe Code RP."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._limiters: Dict[int, _RateLimiter] = {}

    # ------------------------------
    # Rate limiter helper
    # ------------------------------

    def _limiter_for(self, guild_id: int) -> _RateLimiter:
        lim = self._limiters.get(guild_id)
        if not lim:
            lim = _RateLimiter(max_events=8, window_seconds=5)
            self._limiters[guild_id] = lim
        return lim

    # ------------------------------
    # Envio centralizado
    # ------------------------------

    async def _send_log(self, guild: Optional[discord.Guild], embed: discord.Embed):
        if guild is None:
            return

        channel_id = LOG_CHANNEL_ID
        if not channel_id:
            return

        ch = guild.get_channel(channel_id)
        if not isinstance(ch, discord.TextChannel):
            return

        limiter = self._limiter_for(guild.id)
        if not limiter.allow():
            return  # evita flood

        try:
            embed.timestamp = dt.datetime.utcnow()
            await ch.send(embed=embed)
        except Exception:
            return

    # ============================================================
    # LOGS DE MENSAGENS
    # ============================================================

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild is None or getattr(message.author, "bot", False):
            return

        content = message.content or "(mensagem vazia/não cacheada)"

        embed = discord.Embed(
            title="🗑️ Mensagem apagada",
            description=_truncate(content, 1500),
            color=discord.Color.red()
        )
        _brand(embed)

        embed.add_field(name="📍 Canal", value=message.channel.mention, inline=True)
        embed.add_field(
            name="👤 Autor",
            value=f"{message.author.mention} (`{message.author.id}`)",
            inline=True
        )

        if message.attachments:
            files = "\n".join(f"- {a.filename} ({a.size} bytes)" for a in message.attachments)
            embed.add_field(name="📎 Anexos", value=_truncate(files), inline=False)

        await self._send_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.guild is None or getattr(before.author, "bot", False):
            return
        if before.content == after.content:
            return

        embed = discord.Embed(
            title="✏️ Mensagem editada",
            description=f"Canal: {before.channel.mention} | Autor: {before.author.mention}",
            color=discord.Color.orange()
        )
        _brand(embed)

        embed.add_field(name="Antes", value=_truncate(before.content, 900), inline=False)
        embed.add_field(name="Depois", value=_truncate(after.content, 900), inline=False)

        try:
            embed.add_field(name="Jump", value=f"[Clique aqui]({after.jump_url})", inline=False)
        except:
            pass

        await self._send_log(before.guild, embed)

    # ============================================================
    # LOGS DE MEMBROS
    # ============================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild is None or member.bot:
            return

        embed = discord.Embed(
            title="🟢 Membro entrou",
            description=f"{member.mention} (`{member.id}`)",
            color=discord.Color.green()
        )
        _brand(embed)

        embed.add_field(name="Conta criada", value=_fmt_dt(member.created_at))
        embed.add_field(name="ID", value=str(member.id))

        try:
            embed.set_thumbnail(url=member.display_avatar.url)
        except:
            pass

        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild is None or member.bot:
            return

        embed = discord.Embed(
            title="🔴 Membro saiu",
            description=f"{member} (`{member.id}`)",
            color=discord.Color.red()
        )
        _brand(embed)

        try:
            embed.set_thumbnail(url=member.display_avatar.url)
        except:
            pass

        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if after.guild is None or after.bot:
            return

        diffs = []

        if before.nick != after.nick:
            diffs.append(f"🪪 Nick: `{before.nick or '—'}` → `{after.nick or '—'}`")

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added = [r.mention for r in after_roles - before_roles if r.name != '@everyone']
        removed = [r.mention for r in before_roles - after_roles if r.name != '@everyone']

        if added:
            diffs.append("➕ Cargos adicionados: " + ", ".join(added))
        if removed:
            diffs.append("➖ Cargos removidos: " + ", ".join(removed))

        if not diffs:
            return

        embed = discord.Embed(
            title="👤 Atualização de membro",
            description="\n".join(diffs),
            color=discord.Color.blurple()
        )
        _brand(embed)

        embed.add_field(name="Usuário", value=after.mention)

        await self._send_log(after.guild, embed)

    # ============================================================
    # Outros eventos (voz, canais, threads) — mantive seu código original
    # ============================================================
    # (Se quiser, posso reescrever também.)

# =========================================
# Setup
# =========================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Logs(bot))
