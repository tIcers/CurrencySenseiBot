import discord
import os
import ssl
import asyncio
import aiohttp
import certifi
from discord.ext import commands
from const import CURRENCY_CHANNEL_ID, ECON_NEWS_CHANNEL_ID

aiohttp.TCPConnector.ssl = False

os.environ['SSL_CERT_FILE'] = certifi.where()

TOKEN = os.environ.get("TOKEN")
CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY")


intents = discord.Intents.default()
# client = commands.Bot(command_prefix='!', intents=intents)
intents.message_content = True
client = discord.Client(intents=intents)


async def make_request():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://discord.com') as response:
            print(await response.text())


@client.event
async def on_ready():
    print(f"We have logged in as {client.user.name}")
    await make_request()


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send('Hey There!')


# def get_currency_conversion(base_currency, target_currency):
#     url = f'https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/{base_currency}'
#     response = requests.get(url)
#     data = response.json()
#     print(f"{target_currency} to {base_currency} is {data['conversion_rates'][target_currency]}")
#     return data['conversion_rates'][target_currency]
#
#
# async def check_currency_flucturations():
#     channel_id = CURRENCY_CHANNEL_ID
#     previous_rate = None
#     base_currency = 'CAD'
#     target_currency = 'JPY'
#     threshold = 0.6
#
#     while True:
#         rate = get_currency_conversion(base_currency, target_currency)
#         if previous_rate is not None:
#             if abs(rate - previous_rate) >= threshold:
#                 channel = client.get_channel(channel_id)
#                 await channel.send(f'Currency Fluctuation detected: {base_currency}/{target_currency} = {rate}')
#
#         previous_rate = rate
#
#         await asyncio.sleep(3600)
#
#
# async def economic_calender_notification():
#     pass

if __name__ == "__main__":
    # get_currency_conversion('CAD', 'JPY')
    client.run(TOKEN)
