import json
import re
from multiprocessing import Pool

import requests
from requests import RequestException


#获取网页源代码
def get_one_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

#从获取的网页源代码中截取重要的数据
def parse_page(html):
    pattern = re.compile('<dd>.*?board-index.*?">(\d+)</i>.*?data-src="(.*?)".*?</a>'
                         + '.*?name.*?title.*?">(.*?)</a>.*?star">\n\s+(.*?)\n\s+</p>.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'images': item[1],
            'title': item[2],
            'stars': item[3].strip()[3:],
            'releasetime':item[4].strip()[5:],
            'score': item[5] + item[6]
        }

#写入文件
def write_file(content):
    with open('result.txt', 'a', encoding= 'utf-8') as f:
        f.write(json.dumps(content, ensure_ascii= False) + '\n')
        f.close()

#定义主函数
def main(offset):
    url  = 'https://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_page(html):
        print(item)
        write_file(item)

#判断语句
if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])