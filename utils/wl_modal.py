import discord
from discord.ui import Modal, TextInput
from utils.database import db
import os


class WhitelistQuestionsModal(Modal):
    def __init__(self, nome: str, user_id: int):
        super().__init__(title="📘 Whitelist — 10 Perguntas")

        self.nome = nome
        self.user_id = user_id

        self.correct_answers = [
            "a", "b", "c", "a", "d", "b", "a", "c", "b", "d"
        ]

        # Criar campos (TextInput)
        for i in range(1, 11):
            self.add_item(
                TextInput(
                    label=f"Pergunta {i} — Responda A, B, C ou D",
                    placeholder="Digite A, B, C ou D",
                    max_length=1,
                    required=True
                )
            )

    async def on_submit(self, interaction: discord.Interaction):
        answers = []
        correct = 0

        for i, field in enumerate(self.children):
            answer = field.value.lower().strip()
            answers.append(answer)

            if answer == self.correct_answers[i]:
                correct += 1

        percentage = (correct / 10) * 100
        min_score = int(os.getenv("WL_MIN_SCORE", 60))

        result_channel_id = int(os.getenv("WL_RESULT_CHANNEL"))
        approved_role_id = int(os.getenv("WL_APPROVED_ROLE_ID"))

        result_channel = interaction.guild.get_channel(result_channel_id)
        approved_role = interaction.guild.get_role(approved_role_id)

        embed = discord.Embed(
            title="📜 Resultado da Whitelist",
            color=discord.Color.green() if percentage >= min_score else discord.Color.red()
        )

        embed.add_field(name="Nome", value=self.nome, inline=False)
        embed.add_field(name="ID", value=str(self.user_id), inline=False)
        embed.add_field(name="Pontuação", value=f"{percentage:.0f}% ({correct}/10)", inline=False)

        # =======================
        # APROVADO
        # =======================
        if percentage >= min_score:
            embed.add_field(
                name="Status",
                value="✅ **Aprovado!** Bem-vindo à Vhe Code!",
                inline=False
            )

            await db.set_whitelist(self.user_id, 1)

            try:
                await interaction.user.add_roles(approved_role)
            except:
                pass

            if result_channel:
                await result_channel.send(embed=embed)

            await interaction.response.send_message(
                "🎉 Você foi **aprovado**! O canal será encerrado em breve.",
                ephemeral=True
            )

        # =======================
        # REPROVADO
        # =======================
        else:
            embed.add_field(
                name="Status",
                value="❌ **Reprovado.** Você pode tentar novamente depois.",
                inline=False
            )

            if result_channel:
                await result_channel.send(embed=embed)

            await interaction.response.send_message(
                "❌ Você **não atingiu a nota mínima**. Tente novamente.",
                ephemeral=True
            )
