import discord
import os
import ssl
import asyncio
import aiohttp
import certifi
import requests
from discord.ext import commands, tasks
from const import ECON_NEWS_CHANNEL_ID, CURRENCY_CHANNEL_ID

aiohttp.TCPConnector.ssl = False

os.environ['SSL_CERT_FILE'] = certifi.where()

TOKEN = os.environ.get("TOKEN")
CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY")

intents = discord.Intents.default()

intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')
bot_commands = [
        "!convert [base_currency] - Convert currency to JPY",
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


@tasks.loop(seconds=3600)
async def send_converstion_rates_hourly():
    print("send_converstion_rates_hourly function called")
    base_currencies = ['USD', 'CAD']
    target_currency = 'JPY'

    currency_channel = bot.get_channel(CURRENCY_CHANNEL_ID)

    print("currency_channel id is..", currency_channel)

    try:
        print("...send_converstion_rates_hourly...")
        for base_currency in base_currencies:
            if currency_channel:
                rate = get_currency_conversion(base_currency, target_currency)
                await currency_channel.send(f'{base_currency} to {target_currency} is {rate}')
            else:
                print(f"Channel with ID {currency_channel} not found.")
    except Exception as e:
        print(f"An error occurred in the main loop: {e}")


def get_currency_conversion(base_currency, target_currency):
    print("...get_currency_conversion...")
    url = f'https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/{base_currency}'
    response = requests.get(url)
    data = response.json()
    return data['conversion_rates'][target_currency]


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
