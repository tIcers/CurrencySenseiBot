from bs4 import BeautifulSoup
import requests
import os
from const import PROXY_URL, INDEED_URL


def scrape_indeed_jobs():
    session = requests.session()
    proxy = os.getenv("SCRAPE_PROXY")

    page = session.get(
        url=PROXY_URL,
        params={
            'api_key': proxy,
            'url': INDEED_URL, 
        },
    )

    soup = BeautifulSoup(page.content, "html.parser")
    result_contents = soup.find_all('td', class_='resultContent')

    scraped_jobs = []

    for result_content in result_contents:
        job_info = {}
        
        title_element = result_content.find('h2', {'class': 'jobTitle'})
        job_info['title'] = title_element.get_text().strip() if title_element else 'No title found'
        
        company_element = result_content.find('span', attrs={'data-testid': 'company-name'})
        job_info['company'] = company_element.get_text().strip() if company_element else 'No company name found'
        
        location_element = result_content.find('div', attrs={'data-testid': 'text-location'})
        job_info['location'] = location_element.get_text().strip() if location_element else 'No location found'

        salary_element = result_content.find('div', attrs={'data-testid': 'salary-snippet'})
        job_info['salary'] = salary_element.get_text().strip() if salary_element else 'No salary shown'

        a_tag = result_content.find('a')
        job_info['link'] = 'https://ca.indeed.com' + a_tag['href'] if a_tag and a_tag.has_attr('href') else ''

        scraped_jobs.append(job_info)
    print()
    return scraped_jobs

scrape_indeed_jobs()
