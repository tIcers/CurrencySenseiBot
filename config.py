import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
VANCOUVER_TIMEZONE = 'America/Vancouver'

HEADERS = {
        'User-Agent':
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0'
}
