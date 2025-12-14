# utils/wl_views.py

import discord
import asyncio

from utils.wl_session import WLSession
from utils.wl_questions import QUESTIONS
from utils.database import db
from utils.env import (
    WL_MIN_SCORE, WL_APROVADO_ROLE_ID, WL_LOG_CHANNEL_ID,
    FOOTER_LOGO, FOOTER_NOME, WL_CATEGORY_ID
)

SESSIONS = {}  # user_id → WLSession


# ===============================
# EMBED DE PERGUNTA
# ===============================
def build_question_embed(user: discord.Member, question_index: int):
    q = QUESTIONS[question_index]

    embed = discord.Embed(
        title=f"📘 Pergunta {question_index + 1} de {len(QUESTIONS)}",
        description=q["pergunta"],
        color=discord.Color.blue()
    )

    embed.add_field(name="A", value=q["A"], inline=False)
    embed.add_field(name="B", value=q["B"], inline=False)
    embed.add_field(name="C", value=q["C"], inline=False)
    embed.add_field(name="D", value=q["D"], inline=False)

    embed.set_thumbnail(url=FOOTER_LOGO)
    embed.set_footer(text=FOOTER_NOME, icon_url=FOOTER_LOGO)

    return embed


# ===============================
# BOTÕES A/B/C/D
# ===============================
class QuestionButtons(discord.ui.View):
    def __init__(self, user: discord.Member):
        super().__init__(timeout=1200)  # 20 minutos
        self.user = user

    async def _handle_choice(self, interaction, letter):

        # apenas quem está fazendo pode responder
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                "❌ Apenas quem está realizando a whitelist pode responder.",
                ephemeral=True
            )

        session = SESSIONS.get(self.user.id)

        if not session:
            return await interaction.response.send_message(
                "❌ Sessão expirada. Clique no botão e reinicie.",
                ephemeral=True
            )

        session.answer(letter)

        # -------------------------------
        # FINALIZOU TODAS AS PERGUNTAS
        # -------------------------------
        if session.finished:
            score = session.score_percent()
            aprovado = score >= WL_MIN_SCORE

            result = discord.Embed(
                title="📊 Resultado da Whitelist",
                description=(
                    f"**Nome:** {session.user_name}\n"
                    f"**ID:** {session.user_id_db}\n\n"
                    f"**Acertos:** {session.correct}/{len(QUESTIONS)}\n"
                    f"**Pontuação:** **{score}%**\n\n"
                    + ("🎉 **Aprovado!**" if aprovado else "❌ **Reprovado.**")
                ),
                color=discord.Color.green() if aprovado else discord.Color.red()
            )
            result.set_footer(text=FOOTER_NOME, icon_url=FOOTER_LOGO)

            # envia o resultado
            await interaction.response.edit_message(embed=result, view=None)

            # -----------------------------
            # APROVADO → dá cargo e WL no DB
            # -----------------------------
            if aprovado:
                # cargo WL
                role = interaction.guild.get_role(WL_APROVADO_ROLE_ID)
                if role:
                    try:
                        await self.user.add_roles(role)
                    except:
                        pass

                # DB → aplica whitelist
                try:
                    await db.set_whitelist(session.user_id_db, 1)
                except:
                    pass

            # LOG
            log = interaction.guild.get_channel(WL_LOG_CHANNEL_ID)
            if log:
                await log.send(
                    f"📘 **WL Finalizada:** {self.user.mention}\n"
                    f"👤 **Nome:** {session.user_name}\n"
                    f"🆔 **ID:** {session.user_id_db}\n"
                    f"🎯 **Pontuação:** {score}% — {'Aprovado' if aprovado else 'Reprovado'}"
                )

            # APAGAR CANAL EM 1 MINUTO
            await asyncio.sleep(60)
            try:
                await interaction.channel.delete()
            except:
                pass

            return

        # -----------------------------
        # PRÓXIMA PERGUNTA
        # -----------------------------
        next_embed = build_question_embed(self.user, session.current)
        await interaction.response.edit_message(
            embed=next_embed,
            view=QuestionButtons(self.user)
        )

    # Botões
    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def button_a(self, interaction, button): await self._handle_choice(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def button_b(self, interaction, button): await self._handle_choice(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def button_c(self, interaction, button): await self._handle_choice(interaction, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
    async def button_d(self, interaction, button): await self._handle_choice(interaction, "D")


# ===============================
# VIEW INICIAL (painel principal)
# ===============================
class WLButtonView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="📜 Iniciar Whitelist",
        style=discord.ButtonStyle.success,
        custom_id="wl_start"
    )
    async def start(self, interaction: discord.Interaction, button):

        guild = interaction.guild
        category = guild.get_channel(WL_CATEGORY_ID)

        if not category:
            return await interaction.response.send_message(
                "❌ Categoria da whitelist não encontrada.",
                ephemeral=True
            )

        # criar canal privado
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True
            )
        }

        channel = await category.create_text_channel(
            name=f"📜・wl-{interaction.user.name}",
            overwrites=overwrites
        )

        await interaction.response.send_message(
            f"📨 Seu canal foi criado: {channel.mention}",
            ephemeral=True
        )

        # cria sessão
        SESSIONS[interaction.user.id] = WLSession(interaction.user.id)

        # ===============================
        # PERGUNTA 1 → NOME COMPLETO
        # ===============================
        await channel.send(
            embed=discord.Embed(
                title="📝 Etapa 1 — Nome Completo",
                description="Digite **seu nome completo** para registro da whitelist.",
                color=discord.Color.blurple()
            )
        )

        def check_name(msg):
            return msg.channel == channel and msg.author == interaction.user

        msg_name = await self.bot.wait_for("message", check=check_name)
        SESSIONS[interaction.user.id].user_name = msg_name.content.strip()

        # ===============================
        # PERGUNTA 2 → ID DA CIDADE
        # ===============================
        await channel.send(
            embed=discord.Embed(
                title="🆔 Etapa 2 — Seu ID na Cidade",
                description="Digite **apenas o número do seu ID**.",
                color=discord.Color.orange()
            )
        )

        def check_id(msg):
            return msg.channel == channel and msg.author == interaction.user

        msg_id = await self.bot.wait_for("message", check=check_id)
        if not msg_id.content.isdigit():
            await channel.send("❌ ID inválido. Canal será encerrado.")
            await asyncio.sleep(5)
            return await channel.delete()

        SESSIONS[interaction.user.id].user_id_db = int(msg_id.content)

        # ===============================
        # COMEÇA AS PERGUNTAS
        # ===============================
        embed = build_question_embed(interaction.user, 0)
        await channel.send(embed=embed, view=QuestionButtons(interaction.user))
