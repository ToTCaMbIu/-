# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    # атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']

    insta_login = '4zwork'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1622389705:AVVQADwjRqiFqQLZDxY8A4R7blvsRwY9Y2YV5xzcFW6Fg+geRpP6EzK1e4Xoc9RCMn4AzA/a59t07YjSDHDQNb7PPxyAXr85OXzGUKusvE3N1I6uZFrEnIe1mQYLDeTMwJV0CEdyGenMYxo='

    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = 'ziomichael'  # Пользователь, у которого собираем посты. Можно указать список

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    # post_hash = 'eddbde960fed6bde675388aac39a3657'  # hash для получения данных по постах с главной страницы
    followers_hash = '5aefa9893005572d237da5068082d8d5'  # hash для получения данных о подписчиках
    subscr_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'  # hash для получения данных о подписках

    def parse(self, response: HtmlResponse):  # Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:  # Проверяем ответ после авторизации
            yield response.follow(
                # Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                f'/{self.parse_user}',
                callback=self.user_data_parse,
                cb_kwargs={'username': self.parse_user}
            )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}  # 12 постов. Можно больше (макс. 50)
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о подписчиках
        url_subscr = f'{self.graphql_url}query_hash={self.subscr_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о подписках
        yield response.follow(  # собираем подписчиков
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )
        yield response.follow(  # собираем подписки
            url_subscr,
            callback=self.user_subscr_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

    # собираем подписчиков
    def user_followers_parse(self, response: HtmlResponse, username, user_id,
                             variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу

            url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_followers,
                callback=self.user_followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        posts = j_data.get('data').get('user').get('edge_followed_by').get('edges')  # Сами посты
        for post in posts:  # Перебираем подписчиков, собираем данные
            item = InstaparserItem(
                # user_id=post['node']['id'],
                _id=post['node']['id'],
                user_name=post['node']['username'],
                full_name=post['node']['full_name'],
                avatar=post['node']['profile_pic_url'],
                type='follower'
            )
        yield item  # В пайплайн

    # собираем подписки
    def user_subscr_parse(self, response: HtmlResponse, username, user_id,
                          variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу

            url_subscr = f'{self.graphql_url}query_hash={self.subscr_hash}&{urlencode(variables)}'
            yield response.follow(
                url_subscr,
                callback=self.user_subscr_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        posts = j_data.get('data').get('user').get('edge_follow').get('edges')
        for post in posts:  # Перебираем подписки, собираем данные
            # print(post, 'post')
            item = InstaparserItem(
                # user_id=post['node']['id'],
                _id=post['node']['id'],
                user_name=post['node']['username'],
                full_name=post['node']['full_name'],
                avatar=post['node']['profile_pic_url'],
                type='subscr'
            )
            # print(item, 'подписка')
        yield item  # В пайплайн

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
