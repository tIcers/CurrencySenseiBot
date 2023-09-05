import discord
import os
import ssl
import asyncio
import aiohttp
import certifi
import requests
from datetime import datetime
from pytz import timezone
from discord.ext import commands, tasks
from const import ECON_NEWS_CHANNEL_ID, CURRENCY_CHANNEL_ID
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

aiohttp.TCPConnector.ssl = False

os.environ['SSL_CERT_FILE'] = certifi.where()

TOKEN = os.environ.get("TOKEN")
CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY")
API_KEY = os.environ.get("API_KEY")

vancouver_timezone = timezone('America/Vancouver')

intents = discord.Intents.default()

intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')
bot_commands = [
        "!convert [amount] [base_currency] [target_currency]- Convert amount Base to target Currency\n e.g 10000 CAD JPY",
        "!currencies - List major currencies",
        "!help - Show this help message",
]


async def make_request():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://discord.com') as response:
            print("...make_request method...")
            await response.text()


@bot.event
async def on_ready():
    print("...on_ready...")
    print(f"We have logged in as {bot.user.name}")
    currency_channel = bot.get_channel(CURRENCY_CHANNEL_ID)
    print(f"currency_channel:{currency_channel.id}")
    await make_request()
    send_converstion_rates_hourly.start()


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send('Hey There!')

    await bot.process_commands(message)


@bot.command()
async def help(ctx):
    commands_list = "\n".join(bot_commands)

    await ctx.send(f"Available commands:\n```{commands_list}```")


@bot.command()
async def currencies(ctx):
    major_currencies = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY"]

    currency_list = "\n".join(major_currencies)

    await ctx.send(f"Major currencies: \n{currency_list}")


@bot.command()
async def rate(ctx, *args):
    if not args:
        await ctx.send("Please provide the base currency\n (e.g., !rate USD)")
        return

    base_currency = args[0].upper()
    target_currency = 'JPY'
    rate = get_currency_conversion(base_currency, target_currency)
    await ctx.send(f'{base_currency.upper()} To JPY is {rate}')


@bot.command()
async def convert(ctx, *args):
    if not args:
        await ctx.send("Please use the following format to convert currencies:\n"
                       "`!convert [amount] [from_currency] [to_currency]`\n"
                       "For example: `!convert 10000 USD JPY`")
        return

    amount = args[0]
    base_currency = args[1].upper()
    target_currency = args[2].upper()
    result = get_amount_conversion(amount, base_currency, target_currency)
    await ctx.send(f'{amount} {base_currency} = {result} {target_currency}')


def get_amount_conversion(amount, from_currency, to_currency):
    base_url = "https://api.currencybeacon.com/v1/convert"

    params = {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "amount": amount,
    }
    url = f"{base_url}?api_key={API_KEY}"

    response = requests.get(url, params=params)
    data = response.json()
    return data['value']


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


def get_currency_conversion(base_currency, target_currency):
    print("...get_currency_conversion...")
    base_url = 'https://api.currencybeacon.com/v1/latest'

    params = {
        'base': base_currency,
        'symbols': target_currency
    }

    url = f"{base_url}?api_key={API_KEY}"
    response = requests.get(url, params=params)
    data = response.json()
    print("data", data)

    jpy_rate = data['rates'].get(target_currency)
    return jpy_rate


async def check_currency_flucturations():
    channel_id = CURRENCY_CHANNEL_ID
    previous_rate = None
    base_currency = 'CAD'
    target_currency = 'JPY'
    threshold = 0.6

    while True:
        rate = get_currency_conversion(base_currency, target_currency)
        if previous_rate is not None:
            if abs(rate - previous_rate) >= threshold:
                channel = bot.get_channel(channel_id)
                await channel.send(f'Currency Fluctuation detected: {base_currency}/{target_currency} = {rate}')

        previous_rate = rate

        await asyncio.sleep(3600)


async def economic_calender_notification():
    pass


async def main():
    print("...Main function called...")
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
