from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from LMparser.spiders.LM import LMSpider
import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # query = input('')
    process.crawl(LMSpider, query='обои')

    process.start()