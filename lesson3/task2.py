from pymongo import MongoClient


# для вывода на печать значения None
def is_empty(str_val):
    return '' if str_val is None else str_val


# поиск вакансий с заданным минимум зарплаты
def search_by_min_salary(coll, salary_val):
    return coll.find({'$or': [{'MinSalary': {'$gte': salary_val}},
                              {'$and': [{'MinSalary': {'$eq': None}},
                                        {'MaxSalary': {'$gte': salary_val}}
                                        ]
                               }
                              ]
                      }
                     )


client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']
collection = db['vacancy_list']

salary = float(input('Введите желаемую зарплату:\n'))
# Если в вакансии нижняя граница MinSalary указана, то условие запроса salary MinSalary >= salary.
# Если в вакансии не указана нижняя граница, но указана верхняя, то условие запроса MaxSalary >= salary
result = search_by_min_salary(collection, salary)
print(f'{"Название вакансии":<70} {"Мин. зарплата":>14} {"Макс. зарплата":>14} {"Ссылка"}')
for r in result:
    print(f'{r["Name"]:<70} {is_empty(r["MinSalary"]):>14} {is_empty(r["MaxSalary"]):>14} {r["Link"]}')

client.close()
