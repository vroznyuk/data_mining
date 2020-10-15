from bs4 import BeautifulSoup as bs
from bs4 import Comment
import requests
import pandas as pd
from pprint import pprint

# В качестве примера в файл выгружены результаты поиска по запросу "oracle pl/sql",
# обработаны первые 4 страницы результатов

search_string = input('Кем хотите работать?\n')
num_pages = int(input('Сколько страниц просмотреть?\n'))  # здесь можно добавить проверку на вводимое значение

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' + \
                         'Chrome/86.0.4240.75 Safari/537.36'}
list_tmp = []  # для сохранения записей о каждой вакансии

main_link = 'https://www.hh.ru'
current_page = 0
while current_page < num_pages:
    params = {'area': '1',  # Москва
              'st': 'searchVacancy',  # ищем вакансии
              'text': search_string,  # поисковый запрос
              'page': current_page
              }

    response = requests.get(main_link+'/search/vacancy', params=params, headers=headers)
    soup = bs(response.text,'html.parser')
    vacancies = soup.findAll('div', {'class': 'vacancy-serp-item__row_header'})

    # если на странице не нашли тег с искомым классом, значит, вакансии закончились
    if not vacancies:
        break

    for vacancy in vacancies:
        vacancy_link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})  # название
        vacancy_name = vacancy_link.getText()
        vacancy_link = vacancy_link['href']  # ссылка
        salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})  # зарплата
        salary_min = None  # мин зарплата
        salary_max = None  # макс зарплата
        salary_curr = None  # валюта
        if salary:
            salary = salary.text
            # наверное, здесь можно придумать более красивый способ разобрать зарплату,
            # но сейчас уже поздний вечер, и я плохо соображаю
            if salary.startswith('от'):
                salary_min = float(salary.split(' ')[1].replace(u'\xa0', ''))
                salary_curr = salary.split(' ')[2]
            elif salary.startswith('до'):
                salary_max = float(salary.split(' ')[1].replace(u'\xa0', ''))
                salary_curr = salary.split(' ')[2]
            elif salary.find('-') != -1:
                salary_min = float(salary.split(' ')[0].split('-')[0].replace(u'\xa0', ''))
                salary_max = float(salary.split(' ')[0].split('-')[1].replace(u'\xa0', ''))
                salary_curr = salary.split(' ')[1]
            # else во всех остальных случаях None

        list_tmp.append(['HH.ru', vacancy_name, salary_min, salary_max, salary_curr, vacancy_link])
    current_page += 1

main_link = 'https://www.superjob.ru'
current_page = 1
while current_page <= num_pages:
    params = {'keywords': search_string,  # поисковый запрос
              'geo': '4',  # Москва
              'page': current_page
              }

    response = requests.get(main_link+'/vacancy/search/', params=params, headers=headers)
    soup = bs(response.text,'html.parser')
    vacancies = soup.findAll('div', {'class': 'jNMYr'})

    if not vacancies:
        break

    for vacancy in vacancies:
        vacancy_link = vacancy.find('a', {'class': '_6AfZ9'})  # название
        vacancy_name = ''
        for c in vacancy_link.contents:
            vacancy_name += c.string
        vacancy_link = main_link + vacancy_link['href']  # ссылка

        salary = vacancy.find('span', {'class': '_2Wp8I'})  # зарплата
        # удаляем комментарии
        for s in salary.children:
            if isinstance(s, Comment):
                s.extract()

        salary_min = None
        salary_max = None
        salary_curr = None
        # дальше просто катастрофа
        if salary.contents[0].lower() == 'от':
            salary_min = float(salary.contents[2].split(u'\xa0')[0] + salary.contents[2].split(u'\xa0')[1])
            salary_curr = salary.contents[2].split(u'\xa0')[2]
        elif salary.contents[0].lower() == 'до':
            salary_max = float(salary.contents[2].split(u'\xa0')[0] + salary.contents[2].split(u'\xa0')[1])
            salary_curr = salary.contents[2].split(u'\xa0')[2]
        elif (salary.contents[0].lower()).startswith('по'):
            pass
        else:
            salary_min = float(salary.contents[0].replace(u'\xa0', ''))
            salary_max = float(salary.contents[2].replace(u'\xa0', ''))
            salary_curr = salary.contents[4]

        list_tmp.append(['SuperJob.ru', vacancy_name, salary_min, salary_max, salary_curr, vacancy_link])
    current_page += 1

#pprint(list_tmp)

df = pd.DataFrame(list_tmp, columns=['Source', 'Name', 'Min salary', 'Max salary', 'Currency', 'Link'])
df.to_csv('Vacancies.csv', header=True, index=False)
print('Данные сохранены в файл Vacancies.csv')