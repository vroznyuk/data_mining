import requests
from pprint import pprint
import json

ACCESS_TOKEN = ''  # место для Вашего ACCESS_TOKEN
ROOT_LINK = 'https://api.vk.com/method/'

method_name = 'groups.get'
api_link = ROOT_LINK + method_name
api_params = {
    'access_token': ACCESS_TOKEN,
    # 'user_ids': 'durov',  # можно еще id пользователя указать
    'extended': 1,
    'fields': 'description',  # дополнительно - описание сообщества
    'v': '5.52',
}

response = requests.get(api_link, params=api_params)
j_data = response.json()
if j_data.get('error'):
    print('Возникла ошибка:\n')
    pprint(j_data.get('error'))
else:
    with open('resp_task2.json', 'w') as f:
        json.dump(j_data, f)









