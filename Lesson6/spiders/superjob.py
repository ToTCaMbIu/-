import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse):
        vacancies_links = response.xpath("//a[@target='_blank']/@href").extract()

        for i in range(len(vacancies_links)):  # создание полноценных ссылок
            vacancies_links[i] = vacancies_links[i].replace('/vakansii', 'https://russia.superjob.ru/vakansii')

        # next_page = response.css("//a[@class='icMQ_ bs_sM _3ze9n f-test-button-dalshe f-test-link-Dalshe']::attr(href)").extract_first()
        #
        # if next_page:
        #     yield response.follow(next_page, callback=self.parse)
        for vac_link in vacancies_links:
            yield response.follow(vac_link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//title").extract()[0]
        salary = response.xpath("//span[@class='_1h3Zg _2Wp8I _2rfUm _2hCDz']").extract()[0]
        site = 'superjob'
        link = response.xpath("//link[@rel='canonical']/@href").extract()[0]
        yield JobparserItem(name=name, site=site, link=link, salary=salary)
