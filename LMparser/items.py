# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst

def process_photo_links(photo_url):
    correct_url = photo_url.replace('/s/', '/b/').replace('/m/', '/b/')
    return correct_url

class LMParserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    _id = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    char_name = scrapy.Field(output_processor=TakeFirst())
    char_value = scrapy.Field(output_processor=TakeFirst())

