# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class InstagramPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['instagram']

    def process_item(self, item, spider):
        collection = self.db[item['data_type']]
        collection.insert_one(item)
        return item


class InstagramImgPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            try:
                return scrapy.Request(item['photo'])
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item):
        folder_name = item['user_id'] + '_' + item['user_name']  + '/' +\
                      item['data_type'] + '/' +\
                      item['follow_id'] + '_' + item['follow_name'] + '.jpg'
        return folder_name