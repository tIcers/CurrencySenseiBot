import asyncio
import ssl
from datetime import datetime

import aiohttp
from discord.ext import commands, tasks
from dotenv import load_dotenv
from pytz import timezone

import discord
from commands import setup_commands
from const import (CURRENCY_CHANNEL_ID, JOB_CANADA_CHANNEL, JOB_CHANNEL_ID,
                   NEWS_CHANNEL_ID)
from currency_api import get_currency_conversion
from discord import Embed, embeds
from indeed_scraper import scrape_indeed_jobs
from news import get_latest_news

load_dotenv()

toronto_time = timezone("America/Toronto")
intents = discord.Intents.default()

intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

bot.remove_command("help")

bot_commands = [
    "!convert [amount] [base_currency] [target_currency]- Convert amount Base to target Currency\n e.g 10000 CAD JPY",
    "!currencies - List major currencies",
    "!rate - Give you Exchange rate - \n e.g !rate USD JPY",
    "!history [base currency][target_currency][time span] - \n Give you percentage of exchange rate compare to that time"
    "!help - Show this help message",
]
setup_commands(bot)

aiohttp.TCPConnector.ssl = False


async def make_request():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://discord.com") as response:
            print("...make_request method...")
            await response.text()


# @tasks.loop(hours=24)
# async def daily_job_posting():
#     try:
#         vancouver_jobs = scrape_indeed_jobs("Vancouver")
#         canada_jobs = scrape_indeed_jobs("Canada")
#         vancouver_channel = bot.get_channel(JOB_CHANNEL_ID)
#         canada_jobs_channel = bot.get_channel(JOB_CANADA_CHANNEL)
#
#         if vancouver_channel and vancouver_jobs:
#             for job in vancouver_jobs:
#                 await post_job(vancouver_channel, job)
#         if canada_jobs_channel and canada_jobs:
#             for job in canada_jobs:
#                 await post_job(canada_jobs_channel, job)
#
#     except Exception as e:
#         print(f"An error occurred in daily_job_posting: {e}")
#
#
# async def post_job(channel, job):
#     embed = Embed(title=job["title"], url=job["link"], color=0x1A1A1A)
#     embed.add_field(name="Company", value=job["company"], inline=False)
#     embed.add_field(name="Location", value=job["location"], inline=True)
#     embed.add_field(name="Salary", value=job["salary"], inline=True)
#     embed.set_footer(text="Posted on Indeed")
#     await channel.send(embed=embed)
#


@tasks.loop(hours=6)
async def send_converstion_rates_hourly():
    base_currencies = ["USD", "CAD"]
    target_currency = "JPY"
    currency_channel = bot.get_channel(CURRENCY_CHANNEL_ID)

    try:
        current_time = datetime.now(toronto_time)
        if 6 <= current_time.hour <= 22:
            for base_currency in base_currencies:
                if currency_channel:
                    rate = get_currency_conversion(base_currency, target_currency)
                    local_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
                    message = (
                        f"Every Hour Update:\n"
                        f"- Currency Pair: {base_currency} to {target_currency}\n"
                        f"- Exchange Rate: {rate:.2f}\n"
                        f"- Date & Time (UTC): {local_time} GMT"
                    )
                    await currency_channel.send(message)
                else:
                    print(f"Channel with ID {currency_channel} not found.")
        else:
            print("...Skipping message send during quiet hours...")
    except Exception as e:
        print(f"An error occurred in the main loop: {e}")


@tasks.loop(hours=48)
async def daily_news_analysis():
    print("Running daily_news_analysis")
    try:
        news_articles = get_latest_news()
        print(f"Found{len(news_articles)} new articles")
        news_channel = bot.get_channel(NEWS_CHANNEL_ID)

        if news_channel:
            if news_articles:
                for article in news_articles:
                    embed = Embed(title=article["title"], url=article["link"])
                    embed.add_field(name="Date", value=article["date"], inline=False)
                    embed.add_field(
                        name="Summary", value=article["summary"], inline=False
                    )
                    embed.set_footer(text="POsted on Rakuten Securities")
                    await news_channel.send(embed=embed)
            else:
                print("no new articles to show")
        else:
            print(f"Could not find channel with ID: {NEWS_CHANNEL_ID}")
    except Exception as e:
        print(f"An error occured in daily_news_analysis:{e}")


@bot.event
async def on_ready():
    print("...on_ready...")
    print(f"We have logged in as {bot.user.name}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="Currency, News, Jobs.."
        )
    )
    currency_channel = bot.get_channel(CURRENCY_CHANNEL_ID)
    print(f"currency_channel:{currency_channel.id}")
    await make_request()
    print("send_converstion_rates_hourly is starting..")
    send_converstion_rates_hourly.start()
    print("indeed job scraping start...")
    daily_job_posting.start()
    print("send daily_news_analysis")
    daily_news_analysis.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "hello":
        await message.channel.send("Hey There!")

    await bot.process_commands(message)
