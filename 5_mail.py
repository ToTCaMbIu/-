from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from pprint import pprint
from pymongo import MongoClient
import datetime

login = 'study.ai_172@mail.ru'
password = 'NextPassword172!'

client = MongoClient('127.0.0.1', 27017)
db = client['mail']
mail_db = db.mail

options = Options()
options.add_argument('start-maximized')

chromedriver_file = 'chromedriver.exe'

# Переход на страницу
driver = webdriver.Chrome(chromedriver_file, options=options)
driver.get('https://account.mail.ru/login')

# Авторизация
#  Логин
elem = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.NAME, 'username')))
elem.send_keys(login)
elem.send_keys(Keys.ENTER)

#  Пароль
elem = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.NAME, 'password')))
elem.send_keys(password)
elem.send_keys(Keys.ENTER)

# Загрузка списка писем
letters = []
while len(letters) < 20:
    letters = driver.find_elements_by_xpath("//div[@class='dataset__items']/a[contains(@class, 'js-letter-list-item')]")
    sleep(1)

# Сбор ссылок на письма
links = set()
for letter in letters:
    links.add(letter.get_attribute('href'))

# Пролистываем страницу и собираем оставшиеся ссылки
links_count = len(links)
links_count_move = 0
while links_count != links_count_move:
    try:
        links_count = len(links)
        actions = ActionChains(driver)
        actions.move_to_element(letters[-1])
        actions.send_keys(Keys.PAGE_DOWN)
        actions.perform()
        sleep(2)
        letters = driver.find_elements_by_xpath(
            "//div[@class='dataset__items']/a[contains(@class, 'js-letter-list-item')]")
        for letter in letters:
            links.add(letter.get_attribute('href'))
        links_count_move = len(links)
    except Exception as e:
        print(e)
        break

# Собираем содержимое писем
mail_data = []
for link in links:
    driver.get(link)
    mail = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'thread__subject')))
    id = driver.find_elements_by_xpath(
        "//div[contains(@class, 'thread')]/div[contains(@class, 'thread__letter_single')]")
    for el in id:
        text_id = el.get_attribute('data-id')

    header = driver.find_elements_by_class_name('thread__subject')
    for el in header:
        text_header = el.text

    sender = driver.find_elements_by_class_name('letter-contact')
    for el in sender:
        text_sender = el.text
        break

    date = driver.find_elements_by_class_name('letter__date')
    for el in date:
        mail = {}
        text_date = el.text.replace('Сегодня, ', '').replace('Вчера, ', '').replace(' января', '-01') \
            .replace(' февраля', '-02').replace(' марта', '-03').replace(' апреля', '-04') \
            .replace(' мая', '-05').replace(' июня', '-06').replace(' июля', '-07').replace(' августа', '-08') \
            .replace(' сентября', '-09').replace(' октября', '-10').replace(' ноября', '-11') \
            .replace(' декабря', '-12').split(sep=', ')
        if len(text_date) == 1:
            text_date = str(datetime.datetime.now().date()) + " " + str(text_date[0])
            text_date = (datetime.datetime.strptime(text_date, '%Y-%m-%d %H:%M')).timestamp()
        elif len(text_date) == 2:
            text_date[0] = text_date[0].split(sep='-')
            text_date[0] = str(str(datetime.date.today().year) + '-' + text_date[0][1] + '-' + text_date[0][0])
            text_date = (datetime.datetime.strptime(str(text_date[0] + ' ' + text_date[1]), '%Y-%m-%d %H:%M')).timestamp()
        else:
            text_date = 'Ошибка сбора даты/времени!'
    msg = driver.find_elements_by_class_name('letter-body')
    for el in msg:
        text_msg = el.text
    mail['id'] = text_id
    mail['link'] = link
    mail['header'] = text_header
    mail['sender'] = text_sender
    mail['date'] = text_date
    mail['msg'] = text_msg

    mail_data.append(mail)

# Закрытие окна
driver.close()

# Экспорт в БД
for mail in mail_data:
    mail_db.update_one({'_id': mail['id']}, {
        '$set': {'_id': mail['id'], 'link': mail['link'], 'header': mail['header'], 'sender': mail['sender'],
                 'date': mail['date'], 'msg': mail['msg']}}, upsert=True)
