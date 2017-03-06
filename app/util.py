from bs4 import BeautifulSoup
from breadability.readable import Article
from requests import get

def getData(source_url):
    if not source_url.startswith('//') and '://' not in source_url:
        source_url = 'http://' + source_url

    try:
        html = get(source_url, headers={'User-Agent': 'Computer Club Plaintext Reading Plugin'}).text
    except:
        return None, None, None

    soup = BeautifulSoup(html, 'lxml')

    try:
        header = soup.find('h1').text.strip()
    except:
        header = None

    try:
        title = soup.find('title').text.strip()
    except:
        title = None

    readable = Article(html, url=source_url).readable
    soup = BeautifulSoup(readable, 'lxml')

    if not soup.find('div', {'id': 'readabilityBody'}).text.strip():
        readable = None

    return title, header, readable

