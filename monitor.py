import asyncio
import aiohttp
import json
import os
import time
from telegram import Bot
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

# Load websites
with open("config.json") as f:
    WEBSITES = json.load(f).get("websites", [])

status = {url: True for url in WEBSITES}

async def send_message(bot, chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)

async def check_website(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            return response.status == 200, response.status
    except Exception as e:
        return False, str(e)

async def monitor():
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot = bot_app.bot

    async with aiohttp.ClientSession() as session:
        while True:
            for site in WEBSITES:
                is_up, info = await check_website(session, site)
                prev = status.get(site, True)

                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                # Log file
                with open("monitor.log", "a") as f:
                    f.write(f"[{timestamp}] {site}: {'UP' if is_up else 'DOWN'} ({info})\n")

                if is_up and not prev:
                    await send_message(bot, CHAT_ID, f"✅ {site} is back UP! (status: {info})")
                    status[site] = True
                elif not is_up and prev:
                    await send_message(bot, CHAT_ID, f"🚨 {site} appears DOWN! (error/status: {info})")
                    status[site] = False

            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("🚀 Website Monitor started...")
    asyncio.run(monitor())
