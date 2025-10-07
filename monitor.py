import asyncio
import aiohttp
import json
import os
import time
import logging
from telegram import Bot
from dotenv import load_dotenv

# Load env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

# Basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("monitor")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("BOT_TOKEN and CHAT_ID must be set in environment variables.")
    raise SystemExit(1)

bot = Bot(token=BOT_TOKEN)

# Load websites list
with open("config.json") as f:
    WEBSITES = json.load(f).get("websites", [])

# Status dict: True means UP, False means DOWN
status = {url: True for url in WEBSITES}
log_file = "monitor.log"

async def check_website(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            return response.status == 200, response.status
    except Exception as e:
        return False, str(e)

async def monitor_site(session, site):
    is_up, info = await check_website(session, site)
    prev = status.get(site, True)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    # Log to file
    with open(log_file, "a") as lf:
        lf.write(f"[{timestamp}] {site}: {'UP' if is_up else 'DOWN'} ({info})\n")

    if is_up and not prev:
        try:
            bot.send_message(chat_id=CHAT_ID, text=f"✅ {site} is back UP! (status: {info})")
        except Exception as e:
            logger.exception("Failed sending UP message: %s", e)
        status[site] = True
        logger.info("%s is back UP", site)
    elif not is_up and prev:
        try:
            bot.send_message(chat_id=CHAT_ID, text=f"🚨 {site} appears DOWN! (error/status: {info})")
        except Exception as e:
            logger.exception("Failed sending DOWN message: %s", e)
        status[site] = False
        logger.warning("%s appears DOWN (%s)", site, info)
    else:
        logger.info("%s -> %s (%s)", site, 'UP' if is_up else 'DOWN', info)

async def monitor_loop():
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = [monitor_site(session, site) for site in WEBSITES]
            await asyncio.gather(*tasks)
            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    logger.info("Starting async website monitor...")
    try:
        asyncio.run(monitor_loop())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down monitor.")
