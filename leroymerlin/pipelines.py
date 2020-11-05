# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from pymongo import MongoClient
from unidecode import unidecode


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['leroymerlin']

    def process_item(self, item, spider):
        collection = self.db[unidecode(spider.query_txt.replace(' ', '_'))]
        item['link'] = item['link'][0]
        item['properties'] = item['properties'][0]
        collection.insert_one(item)
        return item


class LeroymerlinImgPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for itm in item['photos']:
                try:
                    yield scrapy.Request(itm)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item):
        folder_name = item['link'][0].split('/')[-2] + '/' + request.url.split('/')[-1]
        return folder_name
