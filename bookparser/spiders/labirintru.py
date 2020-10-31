import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%B2%D1%8B%D0%BF%D0%B5%D1%87%D0%BA%D0%B0/']

    def parse(self, response: HtmlResponse):
        main_link = 'https://www.labirint.ru'
        links = response.xpath("//a[@class='product-title-link']/@href").extract()
        next_page = response.xpath("//a[@class='pagination-next__text']/@href").extract_first()
        for link in links:
            yield response.follow(url=main_link + link, callback=self.book_parse)
        if next_page:
            next_page = self.start_urls[0] + next_page
            yield response.follow(url=next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        link = response.url
        name = response.xpath("//h1/text()").extract_first()
        author = response.xpath("//div[@class='authors']/a[@data-event-label='author']/text()").extract_first()
        price = response.xpath("//span[@class='buying-price-val-number' or @class='buying-priceold-val-number']/text()").extract_first()
        price_discount = response.xpath("//span[@class='buying-pricenew-val-number']/text()").extract_first()
        rating = response.xpath("//div[@id='rate']/text()").extract_first()
        yield BookparserItem(link=link, name=name, author=author, price=price, price_discount=price_discount, rating=rating)