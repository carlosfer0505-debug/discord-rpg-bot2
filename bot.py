import os
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from aiohttp import web
from dotenv import load_dotenv
import threading
import asyncio

# ===== Cargar env =====
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
PORT = int(os.getenv("PORT", "8080"))

INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ========= IA DeepSeek ==========

async def deepseek_generate(prompt):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠ Error: {e}"

# ========= EVENTOS DISCORD ==========

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"BOT listo como {bot.user}")

@bot.tree.command(name="ask", description="Pregunta al bot")
async def ask(interaction: discord.Interaction, pregunta: str):
    await interaction.response.defer(thinking=True)
    respuesta = await deepseek_generate(pregunta)
    await interaction.followup.send(respuesta)

@bot.tree.command(name="attack", description="Ataque narrado")
async def attack(interaction: discord.Interaction, accion: str):
    prompt = f"Genera un ataque RPG basado en: {accion}"
    await interaction.response.defer(thinking=True)
    respuesta = await deepseek_generate(prompt)
    await interaction.followup.send(respuesta)

# ========= SERVIDOR WEB PARA RENDER ==========

async def healthcheck(request):
    return web.Response(text="Bot is running", status=200)

def start_webserver():
    async def runner():
        app = web.Application()
        app.router.add_get("/", healthcheck)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

        print(f"Servidor web activo en puerto {PORT}")

        while True:
            await asyncio.sleep(3600)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(runner())

# ========= EJECUCIÓN =========

if __name__ == "__main__":
    threading.Thread(target=start_webserver, daemon=True).start()
    bot.run(DISCORD_TOKEN)
