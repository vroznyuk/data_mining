STOP_FLAG = '*'

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lesson8.instagram import settings
from lesson8.instagram.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    lst_accounts = []
    print(f'Введите список аккаунтов, каждый с новой строки.\nДля окончания введите "{STOP_FLAG}"\n')
    while True:
        user_input = input()
        if user_input == STOP_FLAG:
            break
        if user_input:
            lst_accounts.append(user_input)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider, accounts=lst_accounts)

    process.start()

