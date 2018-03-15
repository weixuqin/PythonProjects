from urllib.parse import urlencode
import pymongo
import requests
from lxml.etree import XMLSyntaxError
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq
from config import *

#配置MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

base_url = 'http://weixin.sogou.com/weixin?'
#添加头文件
headers = {
    'Cookie': 'usid=S-pkM6vW_ac4ktr1; SUV=00A75E9078EFD9F75A6573ECAD0EC883; wuid=AAGCxerSHQAAAAqRGn4SoAgAAAA=; IPLOC=CN4414; SUID=767BEAB73220910A000000005AA9E2AA; pgv_pvi=159197184; pgv_si=s8252565504; ABTEST=0|1521083055|v1; weixinIndexVisited=1; sct=1; JSESSIONID=aaalXqKRP6JjS8ac4Hwhw; ppinf=5|1521083238|1522292838|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo2OiUzQSUyOXxjcnQ6MTA6MTUyMTA4MzIzOHxyZWZuaWNrOjY6JTNBJTI5fHVzZXJpZDo0NDpvOXQybHVOaExNcS1vLW1zbjMxMmNMSkp4OGpZQHdlaXhpbi5zb2h1LmNvbXw; pprdig=tbVf7qLZdDMjpCn4jTf3dg8C8NeRX-YgDi8KUcezn0rteWuhkgU4xMNaxZbakVQuswboIGl_rD-34abU6VY9Jkv7me3BypigyDnIv2lJUchGCo7Gk58m9Qhrm3Aa7NHLHjFVYoaQkQgBSYKpatxMNPe3Tm57ZDlzdPg_8mBmBNQ; sgid=23-30671195-AVqp42ZctqiaCybbDvvfWno4; PHPSESSID=4jjk2a9rv6kq7m50f42r92u3r3; SUIR=D2DF4E12A5A1C3CE1A8AD7F2A5FE18FE; ppmdig=1521087492000000855f9824f94abe82b25d2839135ad3a8; SNUID=FEF36D3F8882EFEC4FCF61E68801DA49; seccodeRight=success; successCount=1|Thu, 15 Mar 2018 04:23:23 GMT',
    'Host': 'weixin.sogou.com',
    'Referer': 'http://weixin.sogou.com/antispider/?from=%2fweixin%3Fquery%3d%E9%A3%8E%E6%99%AF%26type%3d2%26page%3d95%26ie%3dutf8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
}
#初始化代理为本地IP
proxy = None

#定义获取代理函数
def get_proxy():
    try:
        response = requests.get('PROXY_POOL_URL')
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

#添加代理获取网页内容
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


#获取索引页内容
def get_index(keyword, page):
    data = {
        'query': keyword,
        'type': 2,
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html

#解析索引页，提取详情页网址
def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')

#获取详情页
def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

#解析索引页，返回微信文章标题、内容、日期、公众号名称等
def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('.rich_media_title').text()
        content = doc('.rich_media_content').text()
        date = doc('#post-date').text()
        nickname = doc('#js_profile_qrcode > div > strong').text()
        wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        return {
            'title': title,
            'content': content,
            'date': date,
            'nickname': nickname,
            'wechat': wechat
        }
    except XMLSyntaxError:
        return None

#存储到MongoDB，去重操作
def save_to_mongo(data):
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('Saved to Mongo', data['title'])
    else:
        print('Saved to Mongo Failed', data['title'])

#主函数
def main():
    for page in range(1, 101):
        html = get_index(KEYWORD, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_to_mongo(article_data)



if __name__ == '__main__':
    main()