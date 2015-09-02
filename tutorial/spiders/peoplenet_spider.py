# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
import urllib2
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import PeoplenetArticleItem,PeoplenetCommentItem
import MySQLdb
import datetime

class PeoplenetSpider(scrapy.Spider):
    name = 'peoplenet'
    allowed_domains = ['people.com.cn']
    start_urls = []

    s_date = ''
    page_cnt = 1
    dont_filter = False

    '''
    Constructor
    '''
    def __init__(self, search_date = '2015-08-01', *args, **kwargs):
        self.s_date = search_date
        self.start_urls = [self.get_query_url(self.s_date)]
        print self.start_urls

    '''
    Get the query url
    '''
    def get_query_url(self, search_date):
        return 'http://news.people.com.cn/210801/211150/index.js'
        #return 'http://news.people.com.cn/210801/211150/index.js?_=1441184732901'


    def parse(self, response):

        try:
            #Get news.people.com.cn's data
            response = urllib2.urlopen(r'http://news.people.com.cn/210801/211150/index.js')
            #response = urllib2.urlopen(r'http://news.people.com.cn/210801/211150/index.js?_=1441184732901')
            html_utf = response.read()
            #print html_utf

            #transfer to json format
            js = html_utf.replace('{"items":','')
            js_0 = js.replace(']}',']')
            

            hjson = json.loads(js_0)#, encoding="utf-8")
            #print hjson
            for items in hjson:
                
                #news_url = items['url']
                #print items

                article = PeoplenetArticleItem()
                article['aid'] = items['id']
                #date = items['date']

                article['date'] = items['date']
                article['title'] = items['title']
                article['url'] = items['url']#news_url
                
                news_url = items['url']
                req = scrapy.Request(news_url, callback = self.parse_news, dont_filter = self.dont_filter)
                
                req.meta['article'] = article
                yield req
        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!  URL :'
            print traceback.print_exc(file = sys.stdout)




    def parse_news(self, response):
        try:
            #get the rest of the article
            article = response.meta['article']
            agency = response.xpath('//*[@id="p_origin"]/a/text()').extract()
            content = response.xpath('//*[@id="p_content"]/p/text()').extract()
            

            article['agency'] = agency[0]
            article['contents'] = ''.join(content)

            yield response.meta['article']

        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ article['url']
            print traceback.print_exc(file = sys.stdout)
            

            
            
            
            
