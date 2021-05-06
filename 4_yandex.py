from lxml import html
import requests
from pymongo import MongoClient
import datetime

client = MongoClient('127.0.0.1', 27017)
db = client['News']
news = db.news

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'}

response = requests.get('https://yandex.ru/news/', headers=headers)
dom = html.fromstring(response.text)

items = dom.xpath(
    "//div[@class = 'mg-grid__row mg-grid__row_gap_8 news-top-flexible-stories news-app__top']/div[contains(@class, 'mg-grid__col mg-grid__col_xs')]")

for item in items:
    name = item.xpath(".//a//h2[@class = 'mg-card__title']/text()")[0].replace('\xa0', ' ')
    source = item.xpath(".//a[@class = 'mg-card__source-link']/text()")[0]
    link = item.xpath(".//a[@class = 'mg-card__link']/@href")[0]
    date = str(datetime.date.today())

    print(name, link, date)
    document = {'name': name, 'date': date, 'link': link, 'source': source}
    db.news_yandex.insert_one(document)
