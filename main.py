import discord 
import asyncio
import requests 
import os
from dotenv import load_dotenv

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
    print(data['conversion_rates'][target_currency])
    return data['conversion_rates'][target_currency]



if __name__ == "__main__":
    get_currency_conversion('CAD', 'JPY')
