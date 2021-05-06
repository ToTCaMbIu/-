from lxml import html
import requests
from pymongo import MongoClient
import datetime

client = MongoClient('127.0.0.1', 27017)
db = client['News']
news = db.news

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'}

response = requests.get('https://news.mail.ru/', headers=headers)
dom = html.fromstring(response.text)

items = dom.xpath(
    "//table[@class = 'daynews__inner']//td[@class = 'daynews__main'] | //table[@class = 'daynews__inner']//div[@class = 'daynews__item']")

for item in items:
    in_news_item = item.xpath(".//a//@href")[0]
    in_news_response = requests.get(in_news_item, headers=headers)
    dom_in = html.fromstring(in_news_response.text)

    name = dom_in.xpath(".//h1/text()")[0]
    source = dom_in.xpath(".//div[@class = 'breadcrumbs breadcrumbs_article js-ago-wrapper']//span[@class = 'link__text'][1]/text()")[0]
    link = in_news_item
    date = str(datetime.date.today())

    print(name, link, date)
    document = {'name': name, 'date': date, 'link': link, 'source': source}
    db.news_mail.insert_one(document)
