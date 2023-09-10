import requests
import pandas as pd
import datetime
from bs4 import BeautifulSoup as bs


headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
}
url = 'https://tradingeconomics.com/calendar'

response = requests.get(url, headers=headers)

soup = bs(response.content, 'html.parser')

table = soup.find('div', {id: 'calender'})

if table:
    rows = table.find('tbody').find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        cell_data = [cell.get_text(strip=True) for cell in cells]
        print(cell_data)

else:
    print("Table not found on the page")
