# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram

    def process_item(self, item, spider):
        if item['type'] == 'follower':
            collection = self.mongo_base['follower']
            collection.insert_one(item)
            return item
        elif item['type'] == 'subscr':
            collection = self.mongo_base['subscr']
            collection.insert_one(item)
            return item



