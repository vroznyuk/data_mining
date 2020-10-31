# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class BookparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['books']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        if spider.name == 'book24ru':
            if not item['price']:
                item['price'] = float(re.sub('[^\d]', '', item['price_discount']))
                item['price_discount'] = None
            else:
                item['price'] = float(re.sub('[^\d]', '', item['price']))
                item['price_discount'] = float(re.sub('[^\d]', '', item['price_discount']))
            if item['rating']:
                item['rating'] = float(item['rating'].replace(',', '.'))
        elif spider.name == 'labirintru':
            item['name'] = item['name'].split(':')[-1].lstrip()
            if item['price']:
                item['price'] = float(item['price'])
            if item['price_discount']:
                item['price_discount'] = float(item['price_discount'])
            if item['rating']:
                item['rating'] = float(item['rating'])

        collection.insert_one(item)
        return item
