from lxml import html
import requests
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['News']
news = db.news

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'}

response = requests.get('https://lenta.ru/', headers=headers)
dom = html.fromstring(response.text)
source = 'https://lenta.ru/'

items = dom.xpath("//div[@class = 'span4']/div[@class = 'item']")

for item in items:
    name = item.xpath(".//a/text()")[0].replace("xa0", " ")
    link = source + item.xpath(".//a/@href")[0]
    date = item.xpath(".//time/@title")[0]

    print(name, link, date)
    document = {'name': name, 'date': date, 'link': link, 'source': source}
    db.news_lenta.insert_one(document)
