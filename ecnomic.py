import requests
from bs4 import BeautifulSoup
from discord.ext import tasks

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
}

def scrape_economic_calender():
    url = 'https://tradingeconomics.com/calendar'

    with requests.Session() as session:
        session.headers.update(headers)
        page = session.get(url)

        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            parents = soup.find('form', id='aspnetForm')
            container = parents.find('div', class_='container')
            row = container.find('div', class_='row')
            main = row.select_one('div.col-xl-12[role="main"]')
            table = main.find('table', id = 'calendar')
            hd = table.find_all('thead', class_ = 'table-header')

            header_texts = []

            tbody = table.find_all('tbody', class_ = 'table-header')
            print(tbody)


            event_data = []

            for header in hd:
                header_text = ' '.join([th.get_text(strip=True) for th in header.find_all('th')])
                header_texts.append(header_text)
            for text in header_texts:
                print(text)


        else:
            print('failed')


sp = scrape_economic_calender()
print(sp)

