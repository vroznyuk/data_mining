import requests
import json

main_link = 'https://api.github.com/users/vroznyuk/repos'
params = {
    'accept': 'application/vnd.github.v3+json'
}
response = requests.get(main_link, params=params)
j_data = response.json()

# напечатаем для проверки список
for r in j_data:
    print(r.get('full_name'))

with open('resp_task1.json', 'w') as f:
    json.dump(j_data, f)
