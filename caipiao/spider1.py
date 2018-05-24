#-*- coding:utf-8 -*_


#导入相关的库
import requests
import pymysql
from bs4 import BeautifulSoup
from requests import RequestException


#获取索引页
def get_index_page(url):
    try:
        response = requests.get(url)
        response.encoding='utf-8'
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出错')
        return None

#解析索引页
def parse_index_page(html):
    soup = BeautifulSoup(html, 'lxml')
    results = soup.select('.Body .ListRow .ListRow_L a[target]') #可以这样加参，具体到某个 a 标签
    for result in results:
        yield result.attrs['href']

#获取详情页
def get_detail_page(detail_url):
    try:
        response = requests.get(detail_url)
        response.encoding='utf-8'
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错')
        return None

#解析详情页
def parse_detail_page(detail_html):
    soup = BeautifulSoup(detail_html, 'lxml')
    texts = soup.select('#ArticleContent')
    for text in texts:
        yield text.get_text()

def parse_detail_title(detail_html):
    soup = BeautifulSoup(detail_html, 'lxml')
    titles = soup.select('#ArticleTitle')
    for title in titles:
        yield title.get_text()

#保存到本地文件
def save_data(content):
    with open('text.txt', 'a', encoding='utf-8') as f:
        f.write(content)

#存储到 MySQL
def save_mysql(titles, texts):
    # 打开数据库连接
    db = pymysql.connect('localhost', 'root', '', 'caipiao', charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    #SQL 插入语句
    for title in titles:
        for text in texts:
            sql = 'insert into test (title, content) values ("%s", "%s")'
    try:
        # 执行sql语句
        cursor.execute(sql % (title, text))
        print('成功插入数据')
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
        print('插入数据出错')

    # 关闭数据库连接
    db.close()


#定义主函数
def main(offset):
    url = 'https://www.scw98.com/3d/list_3_%d.html' % (offset)
    html = get_index_page(url)
    results = parse_index_page(html)
    for result in results:
        detail_url = 'https://www.scw98.com' + result
        detail_html = get_detail_page(detail_url)
        titles = parse_detail_title(detail_html)
        texts = parse_detail_page(detail_html)
        #save_mysql(titles, texts)
        for text in texts:
            save_data(text)



#定义函数出口
if __name__ == '__main__':
    for i in range(1, 10):
        main(i)