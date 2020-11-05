import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        self.query_txt : str = query
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']
        #self.start_urls = [f'https://leroymerlin.ru/search/?sortby=8&page=29&tab=products&q={query}']


    def parse(self, response: HtmlResponse):
        links = response.xpath("//a[@class='plp-item__info__title']")
        next_page = response.xpath("//div[@class='next-paginator-button-wrapper']/a/@href").extract_first()
        print()
        for link in links:
            yield response.follow(url=link, callback=self.parse_good)
        if next_page:
            yield response.follow(url=next_page, callback=self.parse)

    def parse_good(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_value('link', response.url)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('primary_price', "//uc-pdp-price-view[@class='primary-price']/span[@slot='price']/text()")
        loader.add_xpath('primary_unit', "//uc-pdp-price-view[@class='primary-price']/span[@slot='unit']/text()")
        loader.add_xpath('second_price', "//uc-pdp-price-view[@class='second-price']/span[@slot='price']/text()")
        loader.add_xpath('second_unit', "//uc-pdp-price-view[@class='second-price']/span[@slot='unit']/text()")
        loader.add_xpath('photos', "//picture[@slot='pictures']/img[@itemprop='image']/@src")
        properties = {}
        for itm in response.xpath("//div[@class='def-list__group']"):
            key = itm.xpath('./dt/text()').extract_first()
            val = itm.xpath('./dd/text()').extract_first()
            properties[key] = val.strip()
        loader.add_value('properties', properties)
        yield loader.load_item()


