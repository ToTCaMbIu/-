from pymongo import MongoClient
import json
import pprint

# Запись вакансий в БД
with open('vacancies.json', 'r', encoding='windows-1251') as file:
    vac_list = json.load(file)

client = MongoClient('127.0.0.1', 27017)

db = client['vacancies']
vacancies = db.vacancies

print(f'Вакансий до импорта: {db.vacancies.estimated_document_count()}')
count = db.vacancies.estimated_document_count()

# Добавление уникальных значений в БД
for item in vac_list:
    if vacancies.count_documents({'link': item[0]['link']}) > 0:
        vacancies.update_one({'link': item[0]['link']}, {'$set': item[0]})
        pass
    else:
        vacancies.insert_one(item[0])

print(f'Вакансий после импорта: {db.vacancies.estimated_document_count()}')
count = db.vacancies.estimated_document_count()

# Обработка данных по размеру ЗП
while True:
    try:
        salary = int(input('Введите интересующий размер ЗП:'))
        if salary <= 0:
            raise Exception
        break
    except ValueError:
        print('Неверный формат')
    except Exception:
        print('Введите положительное число')

# Вывод данных по размеру ЗП
counter = 0

for vacansy in vacancies.find({'$or': [{'min': {'$gte': salary}}, {'max': {'$gte': salary}}]}):
    print(vacansy)
