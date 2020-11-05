# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Identity


def convert_price(value: str):
    if value:
        value = float(value.replace(' ', ''))
    else:
        value = None
    return value


class LeroymerlinItem(scrapy.Item):
    _id = scrapy.Field()
    link = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    primary_price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(convert_price))
    primary_unit = scrapy.Field(output_processor=TakeFirst())
    second_price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(convert_price))
    second_unit = scrapy.Field(output_processor=TakeFirst())
    properties = scrapy.Field()
    photos = scrapy.Field(output_processor=Identity())

