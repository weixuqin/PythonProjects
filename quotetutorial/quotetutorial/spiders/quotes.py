# -*- coding: utf-8 -*-
import scrapy

from quotetutorial.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        quotes = response.css('.quote')
        for quote in quotes:
            item = QuoteItem()
            #利用CSS选择器选取想要的信息
            text = quote.css('.text::text').extract_first()
            author = quote.css('.author::text').extract_first()
            tags = quote.css('.tags .tag::text').extract()
            #调用 items.py 中存储的数据结构
            item['text'] = text
            item['author'] = author
            item['tags'] = tags
            yield item

        #实现翻页
        next = response.css('.pager .next a::attr(href)').extract_first()
        url = response.urljoin(next)
        yield scrapy.Request(url=url, callback=self.parse)        #定义回调函数，重新回调自己

