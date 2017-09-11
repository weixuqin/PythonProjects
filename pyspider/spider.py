#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-09-10 15:34:03
# Project: DBmovie

from pyspider.libs.base_handler import *
import pymongo


class Handler(BaseHandler):
    crawl_config = {
    }

    client = pymongo.MongoClient('localhost')
    db = client['trip']
    
    
    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.tripadvisor.cn/Hotels-g274707-Prague_Bohemia-Hotels.html#apg=00f881c271f94bffbb3e45b54b05447b&ss=7F15F66EC5239D49CD6D73370D7D17E7', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('.property_title').items():
            self.crawl(each.attr.href, callback=self.detail_page)
            
        next = response.doc('.pagination .nav.next').attr.href
        self.crawl(next, callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        url = response.url
        name = response.doc('.heading_title').text()
        rating = response.doc('.header_rating .taLnk').text()
        ranking = response.doc('.prw_common_header_pop_index > span').text()
        location = response.doc('.colCnt3').text()
        phone = response.doc('.blEntry.phone > span:nth-child(2)').text()
        grade = response.doc('.overallRating').text()
        return {
            "url": url,
            "name": name,
            "rating": rating,
            "ranking": ranking,
            "location": location,
            "phone": phone,
            "grade": grade
       
        }
    
    def on_result(self, result):
        if result:
            self.save_to_mongo(result)
            
    def save_to_mongo(self, result):
        if self.db['布拉格'].insert(result):
            print('存储到 MongoDB 成功', result)

