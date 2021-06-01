# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import os
import mimetypes
import hashlib
from scrapy.utils.python import to_bytes
from pymongo import MongoClient
import query


class LMparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.LM

    def process_item(self, item, spider):
        item['_id'] = int(item['_id'])
        item['price'] = float(item['price'].replace(' ', ''))

        collection = self.mogo_base[query]
        for i in range(len(item['char_name'])):
            item['char_name'][i] = item['char_name'][i].strip()
        for j in range(len(item['char_value'])):
            item['char_value'][j] = item['char_value'][j].strip()

        properties = dict(zip(item['char_name'], item['char_value']))

        collection.update_one({'_id': item['_id']}, {
            '$set': {'link': item['link'], 'name': item['name'], 'price': item['price'], 'properties': properties,
                     'photos': item['photos']}}, upsert=True)
        return item


class LMPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except TypeError as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        media_ext = os.path.splitext(request.url)[1]

        dir_name = str(item['name']).replace('\\', '_').replace('/', '_').replace(':', '_').replace('*', '_').replace(
            '?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace(' ', '_')
        if media_ext not in mimetypes.types_map:
            media_ext = ''
            media_type = mimetypes.quess_type(request.url)[0]
            if media_type:
                media_ext = mimetypes.guess_extension(media_type)
        return f'{query}/{dir_name}/2000x2000/{media_guid}{media_ext}'
