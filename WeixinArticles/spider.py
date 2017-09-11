from urllib.parse import urlencode
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq

import requests

base_url = 'http://weixin.sogou.com/weixin?'

PROXY_URL = 'http://localhost:5000/get'

proxy = None

MAX_COUNT = 5

headers = {
    'Cookie':'SUV=00A2178F78EF075B5964ECFA8C8C6934; IPLOC=CN4414; SUID=2707EF782E08990A00000000596A40DA; CXID=E24DBA0E0C7E033642A0B386F8E90990; wuid=AAENeExuGgAAAAqLEm/jsgEAIAY=; ad=Q99rFlllll2BPeYXlllllVu4VAtlllllWnD4glllll9lllllxklll5@@@@@@@@@@; ABTEST=3|1504318178|v1; SNUID=4041D38E393F6111679654303A1D4598; weixinIndexVisited=1; JSESSIONID=aaahLcCuvkyg49ASiE24v; PHPSESSID=a6v260kv0qgg1vid2igfkgglc7; SUIR=4041D38E393F6111679654303A1D4598; ppinf=5|1504319482|1505529082|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo2OiUzQSUyOXxjcnQ6MTA6MTUwNDMxOTQ4MnxyZWZuaWNrOjY6JTNBJTI5fHVzZXJpZDo0NDpvOXQybHVOaExNcS1vLW1zbjMxMmNMSkp4OGpZQHdlaXhpbi5zb2h1LmNvbXw; pprdig=rC_X8dxXIzR3wNCEEOmP1t_DejWtLgHrxtrjDLjILpIbImRHS9wUM69BjQKS5Vb94nsUyslukbTZoIDrasV9IGfdqoFsqKs3S2SDXr7Vw0yyn1o_NdbPVi8k43ePA-sUYom99AHUPh30cKlQw16IVBDqbu32tFq8G5dBPc978yI; sgid=23-30671195-AVmqFicoDF64gSe08VDP26zw; ppmdig=150452918000000033e034fc5f9371e86e7661d0921f7b44; sct=9',
    'Host':'weixin.sogou.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
}

def get_proxy():
    try:
        response = requests.get(PROXY_URL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def get_html(url, count=1):
    print('Crawling', url)
    print('Trying Count', count)
    global proxy
    if count >= MAX_COUNT:
        print('Tried Too Many Counts')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            # Need Proxy
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy', proxy)
                return get_html(url)
            else:
                print('Get Proxy Failed')
                return None
    except ConnectionError as e:
        print('Error Occurred', e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url, count)

def get_index(keyword, page):
    data = {
        'query': keyword,
        'type': 2,
        'page': 4
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html

#def parse_index(html):
    #doc = pq(html)
    #items = doc('.news-box .news-list .txt-box h3 a').items()
    #for item in items:
        #yield item.attr('href')


def main():
    for page in range(1, 101):
        html = get_index(' 风景', 1)
        print(html)


if __name__ == '__main__':
    main()

