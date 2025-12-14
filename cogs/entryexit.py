import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone

from utils.env import (
    FOOTER_NOME, FOOTER_LOGO, BANNER_URL,
    ENTRADA_CHANNEL_ID, SAIDA_CHANNEL_ID,
    LOG_CHANNEL_ID, AUTO_ROLE_ID
)

# ============================================================
# PERSONBRAND
# ============================================================

def brand(embed: discord.Embed) -> discord.Embed:
    embed.set_footer(
        text=f"{FOOTER_NOME} • © Todos os direitos reservados.",
        icon_url=FOOTER_LOGO or None
    )
    return embed


def format_datetime(dt: datetime):
    return dt.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")


def account_age(dt: datetime):
    diff = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
    days = diff.days
    hours = diff.seconds // 3600
    if days > 0:
        return f"{days}d {hours}h"
    return f"{hours}h"


# ============================================================
# COG ENTRYEXIT
# ============================================================

class EntryExit(commands.Cog):
    """Sistema de boas-vindas e saída — Vhe Code RP"""

    def __init__(self, bot):
        self.bot = bot

    # ============================================================
    # EMBED DE ENTRADA
    # ============================================================

    def embed_welcome(self, member: discord.Member):
        embed = discord.Embed(
            title=f"{member.name}#{member.discriminator} | Bem-vindo(a)!",
            description=(
                f"Olá {member.mention}, seja muito bem-vindo(a) ao **Vhe Code**! 🌆\n"
                "Esperamos que você tenha uma ótima experiência e aproveite cada momento dentro da cidade.\n\n"
                "Aqui começam suas histórias, suas aventuras e seu RP! 🚓🔥"
            ),
            color=discord.Color.from_str("#0FA3FF")
        )

        thumb = FOOTER_LOGO or BANNER_URL
        if thumb:
            embed.set_thumbnail(url=thumb)

        embed.add_field(
            name="👋 Sabia que…",
            value=f"Você é o **{member.guild.member_count}º membro** aqui no servidor?",
            inline=True
        )

        embed.add_field(
            name="🪪 Tag do Usuário",
            value=f"{member} (`{member.id}`)",
            inline=True
        )

        embed.add_field(
            name="🆘 Precisando de ajuda?",
            value="Se tiver dúvidas ou problemas, **chame nossa equipe!**",
            inline=True
        )

        embed.add_field(
            name="⚠️ Evite punições!",
            value="Leia as nossas regras para evitar problemas no servidor.",
            inline=False
        )

        return brand(embed)

    # ============================================================
    # EMBED DE SAÍDA
    # ============================================================

    def embed_leave(self, member: discord.Member):
        embed = discord.Embed(
            title=f"{member.display_name} saiu do servidor.",
            description=(
                "Obrigado por fazer parte da Vhe Code!\n\n"
                "👤 **Usuário:**\n"
                f"`{member}` (`{member.id}`)\n\n"
                f"🗓 **Conta criada:** `{format_datetime(member.created_at)}` "
                f"({account_age(member.created_at)} atrás)\n"
                f"📥 **Entrou:** `{format_datetime(member.joined_at) if member.joined_at else '—'}`\n\n"
                f"👥 Agora somos `{member.guild.member_count}` membros."
            ),
            color=discord.Color.red()
        )

        logo = FOOTER_LOGO or BANNER_URL
        if logo:
            embed.set_thumbnail(url=logo)

        return brand(embed)

    # ============================================================
    # LOG DE ENTRADA
    # ============================================================

    def embed_join_log(self, member: discord.Member):
        embed = discord.Embed(
            title="🟢 Log — Membro Entrou",
            color=discord.Color.green()
        )

        embed.add_field(name="👤 Usuário", value=f"{member} (`{member.id}`)", inline=False)
        embed.add_field(name="📅 Conta criada", value=f"{format_datetime(member.created_at)} ({account_age(member.created_at)} atrás)", inline=False)
        embed.add_field(name="📥 Entrou", value=format_datetime(member.joined_at), inline=False)
        embed.add_field(name="👥 Total de membros", value=str(member.guild.member_count), inline=False)

        logo = FOOTER_LOGO or BANNER_URL
        if logo:
            embed.set_thumbnail(url=logo)

        return brand(embed)

    # ============================================================
    # ENVIO SEGURO
    # ============================================================

    async def safe_send(self, channel: discord.TextChannel, **kwargs):
        try:
            return await channel.send(**kwargs)
        except:
            await asyncio.sleep(0.3)
            try:
                return await channel.send(**kwargs)
            except:
                return None

    # ============================================================
    # EVENTOS
    # ============================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        cargo = member.guild.get_role(AUTO_ROLE_ID)
        if cargo:
            try:
                await member.add_roles(cargo, reason="Entrada automática")
            except:
                pass

        ch = member.guild.get_channel(ENTRADA_CHANNEL_ID)
        if ch:
            await self.safe_send(ch, content=member.mention, embed=self.embed_welcome(member))

        log_ch = member.guild.get_channel(LOG_CHANNEL_ID)
        if log_ch:
            await asyncio.sleep(0.2)
            await self.safe_send(log_ch, embed=self.embed_join_log(member))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        ch = member.guild.get_channel(SAIDA_CHANNEL_ID)
        if ch:
            await self.safe_send(ch, embed=self.embed_leave(member))

        log_ch = member.guild.get_channel(LOG_CHANNEL_ID)
        if log_ch:
            embed = discord.Embed(
                title="🔴 Log — Membro Saiu",
                description=f"{member} (`{member.id}`)",
                color=discord.Color.red()
            )
            embed = brand(embed)
            await self.safe_send(log_ch, embed=embed)


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(EntryExit(bot))
