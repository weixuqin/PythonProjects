#-*- coding:utf-8 -*-

import requests
from requests import RequestException
from bs4 import BeautifulSoup


def get_page(url):
    try:
        response = requests.get(url)
        response.encoding='utf-8'
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_page(html):
    soup = BeautifulSoup(html, 'lxml')
    results = soup.select('#MainRow_L .MainRow_L_Row .MainRow_KJH')
    for result in results:
        yield result.get_text()


def main():
    url = 'https://www.scw98.com/'
    html = get_page(url)
    texts = parse_page(html)
    for text in texts:
        print(text)

if __name__ == '__main__':
    main()
