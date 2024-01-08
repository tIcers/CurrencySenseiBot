import discord
import aiohttp
import ssl
from datetime import datetime
from pytz import timezone
from discord.ext import commands,tasks
from discord import Embed
from currency_api import get_currency_conversion

from const import CURRENCY_CHANNEL_ID, JOB_CHANNEL_ID
from commands import setup_commands
from dotenv import load_dotenv
from pytz import timezone

from indeed_scraper import scrape_indeed_jobs

load_dotenv()

vancouver_timezone = timezone('America/Vancouver')
intents = discord.Intents.default()

intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command('help')

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
        async with session.get('https://discord.com') as response:
            print("...make_request method...")
            await response.text()

@tasks.loop(hours=12)
async def daily_job_posting():
    try:
        new_jobs = scrape_indeed_jobs()
        channel = bot.get_channel(JOB_CHANNEL_ID)
        if channel:
            for job in new_jobs:
                embed = Embed(title=job['title'], url=job['link'], color=0x1a1a1a)
                embed.add_field(name="Company", value=job['company'], inline=False)
                embed.add_field(name="Location", value=job['location'], inline=True)
                embed.add_field(name="Salary", value=job['salary'], inline=True)
                embed.set_footer(text="Posted on Indeed")
                await channel.send(embed=embed)
        else:
            print(f"Could not find channel with ID {JOB_CHANNEL_ID}")
    except Exception as e:
        print(f"An error occurred during the daily job posting: {e}")

@tasks.loop(hours=1)
async def send_converstion_rates_hourly():
    base_currencies = ['USD', 'CAD']
    target_currency = 'JPY'
    currency_channel = bot.get_channel(CURRENCY_CHANNEL_ID)

    try:
        current_vancouver_time = datetime.now(vancouver_timezone)
        if 6 <= current_vancouver_time.hour <= 22:
            for base_currency in base_currencies:
                if currency_channel:
                    rate = get_currency_conversion(base_currency, target_currency)
                    local_time = current_vancouver_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                    message = (
                        f'Every Hour Update:\n'
                        f'- Currency Pair: {base_currency} to {target_currency}\n'
                        f'- Exchange Rate: {rate:.2f}\n'
                        f'- Date & Time (UTC): {local_time} GMT'
                    )
                    await currency_channel.send(message)
                else:
                    print(f"Channel with ID {currency_channel} not found.")
        else:
            print("...Skipping message send during quiet hours...")
    except Exception as e:
        print(f"An error occurred in the main loop: {e}")


@bot.event
async def on_ready():
    print("...on_ready...")
    print(f"We have logged in as {bot.user.name}")
    await bot.change_presence(
    activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="Currency Exchange"
    )
)
    currency_channel = bot.get_channel(CURRENCY_CHANNEL_ID)
    print(f"currency_channel:{currency_channel.id}")
    await make_request()
    print("send_converstion_rates_hourly is starting..")
    send_converstion_rates_hourly.start()
    print('indeed job scraping start...')
    daily_job_posting.start()

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send('Hey There!')

    await bot.process_commands(message)

