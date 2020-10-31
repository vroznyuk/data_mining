import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%B2%D1%8B%D0%BF%D0%B5%D1%87%D0%BA%D0%B0']
    data = []

    def parse(self, response: HtmlResponse):
        main_link = 'https://book24.ru'
        links = response.xpath("//a[contains(@class, 'book__title-link')]/@href").extract()
        next_page = response.xpath("//a[contains(text(), 'Далее')]/@href").extract_first()
        for link in links:
            yield response.follow(url=main_link+link, callback=self.book_parse)
        if next_page:
            yield response.follow(url=main_link+next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        link = response.url
        name = response.xpath("//h1/text()").extract_first()
        author = response.xpath("//a[@itemprop='author']/text()").extract_first()
        price = response.xpath("//div[@class='item-actions__price-old']//text()").extract_first()
        price_discount = response.xpath("//div[@class='item-actions__price']//text()").extract()[0]
        rating = response.xpath("//span[@class='rating__rate-value']/text()").extract_first()
        yield BookparserItem(link=link, name=name, author=author, price=price, price_discount=price_discount, rating=rating)