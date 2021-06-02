import scrapy
from scrapy.http import HtmlResponse
from LMparser.items import LMParserItem
from scrapy.loader import ItemLoader


class LMSpider(scrapy.Spider):
    name = 'LM'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://leroymerlin.ru']

    def __init__(self, query):
        super(LMSpider, self).__init__()
        self.start_urls = [
            f'https://ekaterinburg.leroymerlin.ru/search/?q={query}&suggest=true']

    def parse(self, response: HtmlResponse):
        goods_links = response.xpath("//a[contains(@href, '/product/') and contains(@tabindex, '-1')]/@href").extract()
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая страница:')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in goods_links:
            yield response.follow(link, callback=self.pasrse_goods)

    def pasrse_goods(self, response: HtmlResponse):
        loader = ItemLoader(item=LMParserItem(), response=response)
        loader.add_xpath('_id', "//span[@slot='article']/@content")
        loader.add_value('link', response.url)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('char_name', "//div/dt/text()")
        loader.add_xpath('char_value', "//div/dd/text()")
        loader.add_xpath('photos', "//uc-pdp-media-carousel/picture/source[contains(@media, '1024')]/@srcset")
        yield loader.load_item()
