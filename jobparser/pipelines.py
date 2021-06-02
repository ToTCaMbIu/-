# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from bs4 import BeautifulSoup

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancies

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        if spider.name == 'hhru':
            item['salary'] = self.normalize_hh(item['salary'])
            collection.insert_one(item)
            return item
        elif spider.name == 'superjob':
            item = self.normalize_sjru(item)
            print(item, 1111)
            collection.insert_one(item)
            return item
        # collection.insert_one(item)



# Обработчик для hhru
    def normalize_hh(self, a):
        salary_vacansy = {'min': '', 'max': '', 'currensy': ''}

        for i in range(len(a)):
            a[i] = a[i].replace('\xa0', '')
            a[i] = a[i].replace('-', ' ')
            a[i] = a[i].replace('.', '')
            a[i] = a[i].replace(' ', '')

        for i in range(len(a)):  # определение валюты
            if len(a[i]) == 3:
                salary_vacansy['currensy'] = a[i]

            if a[i].isdigit() == True:
                a[i] = int(a[i])

        if len(a) > 1:
            try:  # поиск по ключам "от" и "до"
                salary_vacansy['min'] = int(a[a.index('от') + 1])
                salary_vacansy['max'] = int(a[a.index('до') + 1])

            except:
                try:  # поиск по ключу "от"
                    if a.index('от') >= 0:
                        salary_vacansy['min'] = int(a[a.index('от') + 1])
                    elif a.index('до') >= 0:
                        salary_vacansy['max'] = int(a[a.index('до') + 1])
                except:
                    try:  # поиск по ключу "до"
                        if a.index('до') >= 0:
                            salary_vacansy['max'] = int(a[a.index('до') + 1])
                    except:
                        if len(a) and type(a[0]) == int and type(a[1]) == int:
                            salary_vacansy['min'] = int(a[0])
                            salary_vacansy['max'] = int(a[1])
                        else:
                            salary_vacansy['min'] = int(a[0])
                            salary_vacansy['max'] = int(a[0])
        else:
            try:  # для варианта с 1 записью
                if len(a[i]) == 1:
                    if a[i].isdigit() == True:
                        salary_vacansy['min'] = int(a[i])
            except:
                salary_vacansy['min'] = int(a[0])
                salary_vacansy['max'] = int(a[0])
        return salary_vacansy

# Обработчик для sjru
    def normalize_sjru(self, a):
        salary_vacansy = {'min': '', 'max': '', 'currensy': ''}
        for i in a:
            if i == 'link':
                pass
            a[i] = BeautifulSoup(str(a[i]), "lxml").get_text(strip=True)

        for i in a:
            a[i] = a[i].replace('\xa0', '')
            a[i] = a[i].replace(' 000', '000')
            a[i] = a[i].replace('По договорённости', '')
            a[i] = a[i].replace('от', 'от ')
            a[i] = a[i].replace('до', 'до ')
            a[i] = a[i].replace('руб.', ' руб')

        a['salary'] = list(a['salary'].split(' '))

    #обработка части salary
        f_salary = a['salary']
        for i in range(len(f_salary)):  # определение валюты
            if len(f_salary[i]) == 3:
                salary_vacansy['currensy'] = f_salary[i]

            if f_salary[i].isdigit() == True:
                f_salary[i] = int(f_salary[i])

        if len(f_salary) > 1:
            try:  # поиск по ключам "от" и "до"
                salary_vacansy['min'] = int(f_salary[f_salary.index('от') + 1])
                salary_vacansy['max'] = int(f_salary[f_salary.index('до') + 1])

            except:
                try:  # поиск по ключу "от"
                    if f_salary.index('от') >= 0:
                        salary_vacansy['min'] = int(f_salary[f_salary.index('от') + 1])
                    elif f_salary.index('до') >= 0:
                        salary_vacansy['max'] = int(f_salary[f_salary.index('до') + 1])
                except:
                    try:  # поиск по ключу "до"
                        if f_salary.index('до') >= 0:
                            salary_vacansy['max'] = int(f_salary[f_salary.index('до') + 1])
                    except:
                        if len(f_salary) and type(f_salary[0]) == int and type(f_salary[1]) == int:
                            salary_vacansy['min'] = int(f_salary[0])
                            salary_vacansy['max'] = int(f_salary[1])
                        else:
                            salary_vacansy['min'] = int(f_salary[0])
                            salary_vacansy['max'] = int(f_salary[0])
        else:
            try:  # для варианта с 1 записью
                if len(f_salary[i]) == 1:
                    if f_salary[i].isdigit() == True:
                        salary_vacansy['min'] = int(f_salary[i])
            except:
                salary_vacansy['min'] = int(f_salary[0])
                salary_vacansy['max'] = int(f_salary[0])
        a['salary'] = salary_vacansy
        return a

