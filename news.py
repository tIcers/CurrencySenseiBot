import requests 
from discord.ext import commands 
from bs4 import BeautifulSoup

def get_latest_news():
    BASE_NEWS_URL = 'https://media.rakuten-sec.net'
    NEWS_URL= BASE_NEWS_URL + '/category/Kawase-Walker'
    page = requests.get(NEWS_URL)
    soup = BeautifulSoup(page.content, "html.parser")
    latest_article = soup.find_all('div', class_='latest')
    new_articles = []

    for article in latest_article:
        new_marker = article.find('span', class_='new')

        if new_marker and new_marker.get_text(strip=True) == "NEW":
            date_div = article.find('div', class_='date')
            date = date_div.get_text(strip=True) if date_div else None

            title_h2 = article.find('h2', class_='title')
            title = title_h2.get_text(strip=True) if title_h2 else None
            href = title_h2.find('a')['href'] if title_h2 and title_h2.find('a') else None

            summary_p = article.find('p', class_='summary')
            summary = summary_p.get_text(strip=True) if summary_p else None

            if href and href.startswith('/'):
                full_url = BASE_NEWS_URL + href
            else:
                full_url = href
            new_articles.append({
                'date':date, 
                'title':title,
                'summary':summary,
                'link':full_url,
                })
        else:
            print('nothing to show for today')
    return new_articles

