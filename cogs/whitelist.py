from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import traceback

from utils.env import (
    WL_PAINEL_CHANNEL_ID,
    WL_MIN_SCORE,
    FOOTER_LOGO,
    FOOTER_NOME,
    WL_STAFF_ROLE_ID,
)
from utils.wl_views import WLButtonView
from utils.database import db


class WhitelistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[WL] Cog Whitelist carregado.")

    # =====================================================================
    # 🔄 RECRIAR PAINEL — BONITO, PROFISSIONAL E AUTO-CORRETIVO
    # =====================================================================
    async def ensure_panel(self):

        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(WL_PAINEL_CHANNEL_ID)

        if channel is None:
            print("[WL] ERRO: WL_PAINEL_CHANNEL_ID inválido!")
            return

        # Se já existe um painel com botão → NÃO recriar
        async for msg in channel.history(limit=5):
            if msg.author == self.bot.user and msg.components:
                print("[WL] Painel já existe — não recriando.")
                return

        # Caso contrário, recria profissional
        try:
            await channel.purge(limit=10)
        except:
            pass

        embed = discord.Embed(
            title="🎫・Sistema de Whitelist — Vhe Code",
            description=(
                "👋 **Bem-vindo ao sistema de whitelist!**\n\n"
                "Para ingressar na cidade, você passará por um questionário simples, "
                "totalmente automatizado e com botões.\n\n"
                "📝 **Como funciona?**\n"
                "• Clique no botão abaixo.\n"
                "• Um canal privado será criado.\n"
                "• Você terá **20 minutos** para responder tudo.\n"
                "• Ao finalizar, o canal será apagado em **1 minuto**.\n\n"
                f"📌 **Pontuação mínima:** **{WL_MIN_SCORE}%**\n"
                "⚠️ Responda com atenção — você tem apenas uma tentativa."
            ),
            color=discord.Color.from_str("#0fa3ff")
        )

        # IMAGEM DO LADO
        if FOOTER_LOGO:
            embed.set_thumbnail(url=FOOTER_LOGO)

        embed.set_footer(text=FOOTER_NOME, icon_url=FOOTER_LOGO)

        await channel.send(embed=embed, view=WLButtonView(self.bot))
        print("[WL] Painel recriado com sucesso!")

    # =====================================================================
    # EVENTO DE START
    # =====================================================================
    @commands.Cog.listener()
    async def on_ready(self):
        asyncio.create_task(self.ensure_panel())

    # =====================================================================
    # 🔧 /wl — Aprovar whitelist manualmente
    # =====================================================================
    @app_commands.command(name="wl", description="Aprovar manualmente um ID na whitelist.")
    @app_commands.describe(id="ID do jogador no banco")
    async def wl(self, interaction: discord.Interaction, id: int):

        # Verificar permissão
        if WL_STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            return await interaction.response.send_message(
                "❌ Você não possui permissão.",
                ephemeral=True
            )

        try:
            await db.set_whitelist(id, 1)
            await interaction.response.send_message(
                f"✅ Whitelist aprovada para ID **{id}**!",
                ephemeral=True
            )
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(
                f"❌ Erro ao atualizar DB: {e}",
                ephemeral=True
            )

    # =====================================================================
    # 🔧 /remwl — Remover whitelist manualmente
    # =====================================================================
    @app_commands.command(name="remwl", description="Remover whitelist de um ID.")
    @app_commands.describe(id="ID do jogador no banco")
    async def remwl(self, interaction: discord.Interaction, id: int):

        if WL_STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            return await interaction.response.send_message(
                "❌ Você não possui permissão.",
                ephemeral=True
            )

        try:
            await db.set_whitelist(id, 0)
            await interaction.response.send_message(
                f"🗑️ Whitelist removida do ID **{id}**.",
                ephemeral=True
            )
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(
                f"❌ Erro ao remover whitelist: {e}",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(WhitelistCog(bot))
