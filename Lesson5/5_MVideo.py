from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from pprint import pprint
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['mvideo']
mvideo_db = db.mvideo

options = Options()
options.add_argument('start-maximized')

chromedriver_file = 'chromedriver.exe'

# Переход на страницу
driver = webdriver.Chrome(chromedriver_file, options=options)
driver.get('https://mvideo.ru/')

# section = driver.find_element_by_xpath("//div[contains(text(), 'Новинки')]")
section = driver.find_element_by_xpath(
    "//div/h2[@class = 'u-mb-0 u-ml-xs-20 u-hidden-phone gallery-layout__title u-font-normal']")
actions = ActionChains(driver)
actions.move_to_element(section)
actions.perform()

goods = driver.find_elements_by_xpath("//ul[contains(@data-init-param, '\"title\":\"Новинки\"')]/li")
goods_count = len(goods)

# Сбор товаров из карусели
while True:
    button = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH,
                                        "//ul[contains(@data-init-param, '\"title\":\"Новинки\"')]/../../a[@class='next-btn c-btn c-btn_scroll-horizontal c-btn_icon i-icon-fl-arrow-right']")))
    button.click()
    sleep(2)
    goods = driver.find_elements_by_xpath("//ul[contains(@data-init-param, '\"title\":\"Новинки\"')]/li")
    goods_count_click = len(goods)

    if goods_count == goods_count_click:
        break
    goods_count = len(goods)

goods_data = []

# Сбор информации о товарах
for good in goods:
    info = good.find_element_by_class_name('sel-product-tile-title').get_attribute('data-product-info')
    info = json.loads(info)
    info['productPriceLocal'] = float(info['productPriceLocal'])
    info['link'] = 'https://www.mvideo.ru/products/' + info['productId']
    goods_data.append(info)

# Закрытие окна
driver.close()

# Экспорт в БД
for good in goods_data:
    mvideo_db.update_one({'_id': good['productId']}, {
        '$set': {'_id': good['productId'], 'Location': good['Location'], 'eventPosition': good['eventPosition'],
                 'productCategoryId': good['productCategoryId'], 'productCategoryName': good['productCategoryName'],
                 'productGroupId': good['productCategoryName'], 'productName': good['productName'],
                 'productPriceLocal': good['productPriceLocal'], 'productVendorName': good['productVendorName'],
                 'link': good['link']}}, upsert=True)
