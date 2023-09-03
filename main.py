import discord
import os
import ssl
import asyncio
import aiohttp
import certifi
import requests
from discord.ext import commands
from const import CURRENCY_CHANNEL_ID, ECON_NEWS_CHANNEL_ID

aiohttp.TCPConnector.ssl = False

os.environ['SSL_CERT_FILE'] = certifi.where()

TOKEN = os.environ.get("TOKEN")
CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


async def make_request():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://discord.com') as response:
            print(await response.text())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user.name}")
    await make_request()


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send('Hey There!')

    await bot.process_commands(message)


@bot.command()
async def rate(ctx, *args):
    if not args:
        await ctx.send("Please provide the base currency\n (e.g., !rate USD)")
        return

    base_currency = args[0].upper()
    target_currency = 'JPY'
    rate = get_currency_conversion(base_currency, target_currency)
    await ctx.send(f'{base_currency.upper()} To JPY is {rate}')


def get_currency_conversion(base_currency, target_currency):
    url = f'https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/{base_currency}'
    response = requests.get(url)
    data = response.json()
    print(f"{target_currency} to {base_currency} is {data['conversion_rates'][target_currency]}")
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

if __name__ == "__main__":
    bot.run(TOKEN)
