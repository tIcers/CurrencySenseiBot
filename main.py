import discord
import asyncio
import requests
import os
from dotenv import load_dotenv
from const import CURRENCY_CHANNEL_ID, ECON_NEWS_CHANNEL_ID

load_dotenv()

TOKEN = os.getenv("TOKEN")
CURRENCY_API_KEY=os.getenv("CURRENCY_API_KEY")

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)


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
                channel = client.get_channel(channel_id)
                await channel.send(f'Currency Fluctuation detected: {base_currency}/{target_currency} = {rate}')

        previous_rate = rate

        await asyncio.sleep(360)


        if abs(rates - )
if __name__ == "__main__":
    get_currency_conversion('CAD', 'JPY')
