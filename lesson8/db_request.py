# 4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
# 5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
from pymongo import MongoClient
from pprint import pprint

user_name = input('Введите имя пользователя:\n')
if user_name:
    client = MongoClient('localhost', 27017)
    db = client['instagram']
    # подписчики заданного пользователя
    followers = db['followers'].find({'user_name': user_name})
    print('=== П О Д П И С Ч И К И ===')
    for f in followers:
        pprint(f)

    # подписки заданного пользователя
    following = db['following'].find({'user_name': user_name})
    print('=== П О Д П И С К И ===')
    for f in following:
        pprint(f)

    client.close()



