import discord
import aiohttp
import ssl
from datetime import datetime
from pytz import timezone
from discord.ext import commands,tasks

from currency_api import get_currency_conversion

from const import CURRENCY_CHANNEL_ID
from commands import setup_commands
from dotenv import load_dotenv
from pytz import timezone

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

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send('Hey There!')

    await bot.process_commands(message)

