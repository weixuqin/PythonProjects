# -*- coding: utf-8 -*-

#定义存储数据的格式，定义新的 scrapy 默认函数等, 需要在setting.py中指定具体的pipeline才会生效
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import pymongo


class TextPipeline(object):
    #对 item （存储的数据）进行处理（定义格式、长度等等，存储的数据库）

    def __init__(self):
        self.limit = 50

    def process_item(self, item, spider):
        if item['text']:
            if len(item['text']) > self.limit:
                item['text'] = item['text'][0:self.limit].rstrip() + '...'
            return item
        else:
            return DropItem('Missing text')

#存储到 MongoDB
class MongoDBPipeline(object):

    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    #定义 scrapy 的默认参数
    #类方法
    @classmethod
    def from_crawl(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    #定义一个对MongoDB初始化对象的声明函数
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    #MongoDB插入数据
    def process_item(self, item, spider):
        name = item.__class__.__name__
        self.db['name'].insert(dict(item))
        return item

    #定义一个关闭 MongoDB 进程函数
    def close_spider(self, spider):
        self.client.close()
