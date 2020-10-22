import requests
import time
from lxml import html
from datetime import date, datetime, timedelta
from pymongo import MongoClient
from pprint import pprint

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                         ' Chrome/86.0.4240.75 Safari/537.36'}

news_list = []


# функция добавления новых записей в БД
def db_insert_if_not_exists(coll, data):
    coll.update_one({'Link': data.get('Link')}, {'$set': data}, upsert=True)
    # news_list.append(dict_tmp)


# получение DOM
def get_dom(link, params):
    time.sleep(1)
    response = requests.get(link, params=params, headers=HEADERS)
    return html.fromstring(response.text)


# получение времени и источника новости на Mail.ru
def get_attrs_mailru(link):
    root = get_dom(link, {})
    time_ = datetime.strptime(root.xpath("//div[contains(@class,'breadcrumbs')]//" +
                                         "span[contains(@class,'js-ago')]/@datetime")[0],
                              '%Y-%m-%dT%H:%M:%S%z')
    source_ = root.xpath("//div[contains(@class,'breadcrumbs')]//span[@class='link__text']/text()")[0]
    return time_, source_


# получение времени новости на Lenta.ru
def get_time_lentaru(link):
    root = get_dom(link, {})
    time_ = datetime.strptime(root.xpath("//div[@class='b-topic__info']/time/@datetime")[0], '%Y-%m-%dT%H:%M:%S%z')
    return time_


client = MongoClient('127.0.0.1', 27017)
db = client['daily_news']
collection = db['news_list']

dict_tmp = {}

print('Поехали...')

# Яндекс.Новости
main_link = 'https://news.yandex.ru'
dom = get_dom(main_link, {})
result = dom.xpath("//article[contains(@class,'mg-grid__item_type_card')]")
for itm in result:
    news_link = itm.xpath(".//a/@href")[0]
    news_header = itm.xpath(".//h2[@class='news-card__title']/text()")[0]
    news_time = itm.xpath(".//span[@class='mg-card-source__time']/text()")[0]
    # Возможно, тут могут быть варианты (позавчера, 2 дня назад и тп),
    # но так глубоко я не копала. Наверное, интересные ошибки можно получить,
    # если запускать скрипт после 12 ночи
    if news_time.startswith('вчера'):
        news_dt = date.today() - timedelta(days=1)
        news_time = news_time[8:]
    else:
        news_dt = date.today()

    news_time = datetime.combine(news_dt, datetime.strptime(news_time, '%H:%M').time())
    news_source = itm.xpath(".//span[@class='mg-card-source__source']/a/text()")[0]
    dict_tmp = {'Source': news_source, 'Header': news_header, 'Link': news_link, 'Time': news_time}
    db_insert_if_not_exists(collection, dict_tmp)

# Новости Mail.ru
main_link = 'https://news.mail.ru'
dom = get_dom(main_link, {})
# новости дня - в картинках
result = dom.xpath("//div[contains(@class, 'daynews__item')]")
for itm in result:
    news_link = itm.xpath("./a/@href")[0]
    news_header = itm.xpath(".//span[contains(@class, 'photo__title')]/text()")[0].replace(u'\xa0', ' ')
    news_time, news_source = get_attrs_mailru(news_link)
    dict_tmp = {'Source': news_source, 'Header': news_header, 'Link': news_link, 'Time': news_time}
    db_insert_if_not_exists(collection, dict_tmp)

# блок новостей под картинками
result = dom.xpath("//ul[contains(@class, 'list')][@data-module='TrackBlocks']/li[@class='list__item']")
for itm in result:
    news_link = itm.xpath(".//a/@href")[0]
    news_header = itm.xpath(".//a/text()")[0].replace(u'\xa0', ' ')
    news_time, news_source = get_attrs_mailru(news_link)
    dict_tmp = {'Source': news_source, 'Header': news_header, 'Link': news_link, 'Time': news_time}
    db_insert_if_not_exists(collection, dict_tmp)

# новости дня по основным разделам
result = dom.xpath("//div[@class='cols__inner']")
for itm in result:
    news_link = itm.xpath(".//a[contains(@class, 'newsitem__title')]/@href")[0]
    news_header = itm.xpath(".//span[contains(@class, 'newsitem__title-inner')]/text()")[0].replace(u'\xa0', ' ')
    news_time, news_source = get_attrs_mailru(news_link)
    dict_tmp = {'Source': news_source, 'Header': news_header, 'Link': news_link, 'Time': news_time}
    db_insert_if_not_exists(collection, dict_tmp)

    for itm_child in itm.xpath(".//span[@class='list__text']"):
        news_link = itm_child.xpath(".//a/@href")[0]
        news_header = itm_child.xpath(".//span/text()")[0].replace(u'\xa0', ' ')
        news_time, news_source = get_attrs_mailru(news_link)
        dict_tmp = {'Source': news_source, 'Header': news_header, 'Link': news_link, 'Time': news_time}
        db_insert_if_not_exists(collection, dict_tmp)

# Lenta.ru - Главные новости
main_link = 'https://lenta.ru'
dom = get_dom(main_link, {})
result = dom.xpath("//div[@class='b-yellow-box__wrap']/div[@class='item']")
for itm in result:
    news_link = main_link + itm.xpath("./a/@href")[0]
    news_header = itm.xpath("./a/text()")[0].replace(u'\xa0', ' ')
    news_time = get_time_lentaru(news_link)
    news_source = 'Lenta.ru'
    dict_tmp = {'Source': news_source, 'Header': news_header, 'Link': news_link, 'Time': news_time}
    db_insert_if_not_exists(collection, dict_tmp)

print('Готово!')
# pprint(news_list)
