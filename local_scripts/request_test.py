import requests
import json

user = 'api_test'
pwd = 'apikeyforpython'

r = requests.get('http://127.0.0.1:8000/api/users', auth=(user, pwd))
print(f'JSON:\n{json.dumps(r.json(), indent=4)}')
