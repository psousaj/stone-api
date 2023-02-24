import json
import os
from connection.fetch_api import FetchApi

api = FetchApi(base_url='sandBox')
api.get_access_token()
# api.permit_client(requestType='T', filiates=[])

path = os.getcwd()
path += r'\connection\access\company-tokens\token-{}.json'.format(api.stone_code)
print(path)
with open(path, 'r') as file:
    dic = json.load(file)

api.get_status_client(dic['requestId'])
