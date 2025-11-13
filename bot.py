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
PORT = int(os.getenv("PORT", 8080))

INTENTS = discord.Intents.default()
INTENTS.message_content = True
bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ======== IA DeepSeek ========
async def deepseek_generate(prompt: str) -> str:
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            return f"⚠️ Error en la API:\n```json\n{data}\n```"

# ===== DISCORD =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"BOT LISTO como {bot.user}")

@bot.tree.command(name="ask", description="Pregunta al bot")
async def ask(interaction: discord.Interaction, pregunta: str):
    await interaction.response.defer(thinking=True)
    respuesta = await deepseek_generate(pregunta)
    await interaction.followup.send(respuesta)

@bot.tree.command(name="attack", description="Ataque narrado")
async def attack(interaction: discord.Interaction, accion: str):
    prompt = f"Describe un ataque de rol: {accion}. Sé épico y breve."
    await interaction.response.defer(thinking=True)
    respuesta = await deepseek_generate(prompt)
    await interaction.followup.send(respuesta)

# ======== SERVIDOR WEB PARA RENDER ========
async def handle(request):
    return web.Response(text="Bot is running", content_type="text/plain")

def start_web_server():
    async def _run():
        app = web.Application()
        app.router.add_get("/", handle)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

        print(f"Servidor web activo en puerto {PORT}")

        while True:
            await asyncio.sleep(3600)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_run())

if __name__ == "__main__":
    threading.Thread(target=start_web_server).start()
    bot.run(DISCORD_TOKEN)
