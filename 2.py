import json

from bs4 import BeautifulSoup as bs
import requests
from my_functions import normalize

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'}

number = 0
search = 'Python'  # input('Какой запрос?')
main_url = f'https://ekaterinburg.hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text={search}&page={number}'

page_limit = 40  # input('Сколько страниц анализируем?')
number = 0  # input('К какой странице обращаемся?')

for number in range(0, page_limit + 1):  # перебираем страницы результата поиска
    response = requests.get(main_url, headers=headers)

    dom = bs(response.text, 'html.parser')

    vac_list = dom.find_all('div', {'class': 'vacancy-serp-item'})

    vacancies = []
    for vacansy in vac_list:  # собираем информацию о вакансиях в список

        salary_vacansy = {}
        list_sal_vac = []
        vac_name = vacansy.find('a', {'class': 'bloko-link HH-LinkModifier'}).text
        vac_link = vacansy.find('a', {'class': 'bloko-link HH-LinkModifier'})['href']

        salary = vacansy.find('div', {'class': 'vacancy-serp-item__sidebar'}).getText()
        salary = salary.replace('\xa0', '')
        salary = salary.replace('-', ' ')

        salary_vacansy['name'] = vac_name
        salary_vacansy['link'] = vac_link

        norm_salary = salary  # определение переменной для функции
        for i in normalize(norm_salary):  # внесение в список нормализованных даенных
            salary_vacansy[i] = normalize(norm_salary)[i]

            vacancies.append(salary_vacansy)

    file_name = 'vacancies.json'

    with open('vacancies.json', 'w+') as file:  # сохраниение результата в файл
        json.dump(vacancies, file, ensure_ascii=False)
