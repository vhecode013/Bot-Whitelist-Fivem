import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# ================================
# LOAD ENV
# ================================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
APP_ID = os.getenv("DISCORD_APP_ID")

if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN não encontrado no .env")

if not APP_ID:
    raise RuntimeError("❌ DISCORD_APP_ID não encontrado no .env")

APP_ID = int(APP_ID)

# ================================
# INTENTS
# ================================
intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=None,
    intents=intents,
    help_command=None,
    application_id=APP_ID   # NECESSÁRIO para slash commands
)

# ================================
# IMPORTA VIEWS PERSISTENTES
# ================================
from utils.wl_views import WLButtonView


# ================================
# LOAD COGS AUTOMATICAMENTE
# ================================
async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            name = file[:-3]
            try:
                await bot.load_extension(f"cogs.{name}")
                print(f"[COG] Carregado: {name}")
            except Exception as e:
                print(f"[ERRO] Falha ao carregar {name}: {e}")


# ================================
# on_ready — SYNC REAL e ESTÁVEL
# ================================
@bot.event
async def on_ready():

    # registra views persistentes (essencial)
    bot.add_view(WLButtonView(bot))

    # atraso para o Discord registrar a aplicação
    await asyncio.sleep(1.5)

    # tenta syncar em segurança
    try:
        synced = await bot.tree.sync()
        print(f"🌎 Slash Commands sincronizados: {len(synced)}")
    except Exception as e:
        print("[ERRO] Sync falhou:", e)

    print(f"🤖 Bot online como: {bot.user}")
    print("Vhe Code RP — Online e operando!")


# ================================
# MAIN — EXECUÇÃO DO BOT
# ================================
async def main():

    # carrega todas as cogs
    await load_cogs()

    # inicia o bot
    await bot.start(TOKEN)


asyncio.run(main())
