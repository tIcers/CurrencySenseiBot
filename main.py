import discord
import os
import ssl
import asyncio
import aiohttp
import certifi
import requests
import json
from datetime import datetime, date, timedelta
from pytz import timezone
from discord.ext import commands, tasks
from const import  CURRENCY_CHANNEL_ID
from dotenv import load_dotenv

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
        "!rate - Give you Exchange rate - \n e.g !rate USD JPY",
        "!history [base currency][target_currency][time span] - \n Give you percentage of exchange rate compare to that time"
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
    await bot.change_presence(
    activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="Currency Exchange"
    )
)
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
async def rate(ctx, *args):
    if not args:
        await ctx.send("Please provide the base currency\n (e.g., !rate USD)")
        return

    base_currency = args[0].upper()
    target_currency = args[1].upper()
    rate = get_currency_conversion(base_currency, target_currency)
    await ctx.send(f'{base_currency.upper()} To {target_currency.upper()} is {rate}')


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


@bot.command()
async def currencies(ctx):
    major_currencies = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY"]

    currency_list = "\n".join(major_currencies)
    get_currencies('fiat')

    await ctx.send(f"Major currencies: \n{currency_list}")


def get_currencies(type_of_currency):
    base_url = "https://api.currencybeacon.com/v1/currencies"
    params = {
        "type": type_of_currency
    }
    url = f"{base_url}?api_key={API_KEY}"
    response = requests.get(url, params=params)
    data = response.json()
    formatted_json = json.dumps(data, indent=4)
    print(formatted_json)
    return data


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

    rate = data['rates'].get(target_currency)
    return rate


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


@bot.command()
async def history(ctx, base_currency, target_currency, time_span):
    print("....Enter the function...")
    if time_span not in ["1d", "1w", "1y", "5y", "10y"]:
        await ctx.send("Invalid time span. Please use 1d, 1w, 1y, 5y or 10y")

    end_date = date.today()
    if time_span == "1d":
        print("...1d...")
        start_date = end_date - timedelta(days=1)
        print('start date for 1d', start_date)
    elif time_span == "1w":
        print("...1w...")
        start_date = end_date - timedelta(weeks=1)
        print('start date for 1w', start_date)
    elif time_span == "6m":
        start_date = end_date - timedelta(weeks=26)
        print('start date for 6m', start_date)
    elif time_span == "1y":
        print("...1y...")
        start_date = end_date - timedelta(days=365)
    elif time_span == "5y":
        print("...5y...")
        start_date = end_date - timedelta(days=5 * 365)
    elif time_span == "10y":
        print("...10y...")
        start_date = end_date - timedelta(days=10 * 365)

    historical_data = get_historical_data(base_currency, target_currency, start_date)
    print("...historical data... creating...", historical_data)
    if not historical_data:
        await ctx.send("Failed to fetch historical data")
        return

    current_currency_rate =  get_currency_conversion(base_currency, target_currency)

    percentage_change = ((current_currency_rate - historical_data ) / historical_data) * 100
    await ctx.send(f"The exchange rate for {base_currency}/{target_currency} changed by {percentage_change:.2f}% over the past {time_span}.")


def get_historical_data(base_currency, target_currency, start_date):
    print('...fetching history data....')
    historical_url = "https://api.currencybeacon.com/v1/historical"

    params = {
        "base": base_currency,
        "date": start_date.strftime("%Y-%m-%d"),
        "symbols": target_currency,
    }

    url = f"{historical_url}?api_key={API_KEY}"
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        print("HISTORICAL DATA", data)
        historical_rates = data.get("response", {}).get("rates", {}).get(target_currency)
        return historical_rates
    else:
        print(f"Failed to fetch historical data. Status code: {response.status_code}")
        return None


# async def economic_calender_notification():
#     pass


async def main():
    print("...Main function called...")
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
