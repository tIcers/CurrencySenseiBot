import os
import requests
from dotenv import load_dotenv
from const import CURRENCY_CHANNEL_ID

CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
load_dotenv()

CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY")
API_KEY = os.environ.get("API_KEY")
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
