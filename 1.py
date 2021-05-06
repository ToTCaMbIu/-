import requests
import json
from pprint import pprint

name = 'ToTCaMbIu'
link = 'https://api.github.com/users/' + name + '/repos'

response = requests.get(link)

data = response.json()
with open('repos.json', 'w') as f:
    file = json.dump(data, f, indent=4)

with open('repos.json', 'r') as f:
    file = json.load(f)

    print('Список репозиториев:')
    for repo in file:
        pprint(repo['name'])
