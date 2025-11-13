import os
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

INTENTS = discord.Intents.default()
INTENTS.message_content = True  # permite leer menciones y textos

bot = commands.Bot(command_prefix="!", intents=INTENTS)


# ---------------------------
#  IA (DeepSeek)
# ---------------------------

async def deepseek_generate(prompt: str) -> str:
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]


# ---------------------------
#   EVENTO DE INICIO
# ---------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"BOT EN LÍNEA como: {bot.user}")


# ---------------------------
#   COMANDO /ask (ChatGPT)
# ---------------------------

@bot.tree.command(name="ask", description="Hazle una pregunta al bot.")
async def ask(interaction: discord.Interaction, pregunta: str):
    await interaction.response.defer(thinking=True)

    respuesta = await deepseek_generate(pregunta)
    await interaction.followup.send(f"**Respuesta:**\n{respuesta}")


# ---------------------------
#   COMANDOS DE ROL
# ---------------------------

@bot.tree.command(name="attack", description="Realiza un ataque narrado.")
async def attack(interaction: discord.Interaction, accion: str):
    prompt = f"Describe un ataque de rol: {accion}. Sé narrativo pero breve."
    await interaction.response.defer(thinking=True)
    respuesta = await deepseek_generate(prompt)
    await interactio
