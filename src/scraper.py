import requests
from bs4 import BeautifulSoup

def parse_news(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    headlines = []
    for item in soup.find_all('h2'):
        headlines.append(item.get_text())
    return headlines

def fetch_news(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None
