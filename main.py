import os
import asyncio
import certifi
import json
from bot import bot
from datetime import datetime, date, timedelta
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

os.environ['SSL_CERT_FILE'] = certifi.where()


async def main():
    print("...Main function called...")
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
