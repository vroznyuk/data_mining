import scrapy
import re
import json
from scrapy.http import HtmlResponse
from lesson8.instagram.items import InstagramItem
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login = 'serpentina.lettuce'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1604760364:AaRQAJffByuyZhsZ26bKe6FpF/7SUbCWJZZtzXU2C/qkzzoXWtJnVUaz61a+L827PvrYbijhAGvDZD0RHACmuTcRedst+2NnBAiD+W8h5BAq3sSZrBKxY5MaKgVywaFnWABM4HP7K8EzWZ1dLDvF'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076'  # подписки
    followers_hash = 'c76146de99bb02f6415203be841dd25a'  # подписчики

    def __init__(self, accounts):
        self.lst_accounts = accounts

    def parse(self, response):
        csrf_token = self.fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
                self.inst_login_link,
                method='POST',
                callback=self.auth,
                formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
                headers={'X-CSRFToken': csrf_token}
            )

    def auth(self, response:HtmlResponse):
        jdata = json.loads(response.text)
        if jdata['authenticated']:                 #Проверяем ответ после авторизации
            for accnt in self.lst_accounts:
                yield response.follow(             #Переходим на страницу пользователя
                        f'/{accnt}/',
                        callback= self.user_data_parse,
                        cb_kwargs={'username': accnt}
                    )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'first': 12}

        url_posts = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
        yield response.follow(
                url_posts,
                callback=self.user_follow_parse,
                cb_kwargs={'username': username,
                            'user_id': user_id,
                            'query_hash': self.following_hash,
                            'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
            )

        variables = {'id': user_id,
                     'first': 12}
        url_posts = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        yield response.follow(
                url_posts,
                callback=self.user_follow_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'query_hash': self.followers_hash,
                           'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
            )

    def user_follow_parse(self, response: HtmlResponse, username, user_id, query_hash, variables):
        jdata = json.loads(response.text)
        if query_hash == self.followers_hash:
            page_info = jdata.get('data').get('user').get('edge_followed_by').get('page_info')
        elif query_hash == self.following_hash:
            page_info = jdata.get('data').get('user').get('edge_follow').get('page_info')

        if page_info.get('has_next_page'):  # Если есть еще подписки/подписчики
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_posts = f'{self.graphql_url}query_hash={query_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_follow_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'query_hash': query_hash,
                           'variables': deepcopy(variables)}
            )
        if query_hash == self.followers_hash:
            edges = jdata.get('data').get('user').get('edge_followed_by').get('edges')
            data_type = 'followers'
        elif query_hash == self.following_hash:
            edges = jdata.get('data').get('user').get('edge_follow').get('edges')
            data_type = 'following'

        for edge in edges:  # Перебираем посты, собираем данные
            item = InstagramItem(
                data_type=data_type,
                user_id=user_id,
                user_name=username,
                follow_id=edge['node']['id'],
                follow_name=edge['node']['username'],
                follow_full_name=edge['node']['full_name'],
                photo=edge['node']['profile_pic_url'],
                post=edge['node']
            )
            yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
        return json.loads(matched).get('id')