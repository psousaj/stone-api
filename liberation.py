from connection.fetch_api import FetchApi
from configs.logging_config import logger
import sys
import argparse
import os
import json

parser = argparse.ArgumentParser(description='Liberar acesso a uma determinada empresa')
parser.add_argument('--number', nargs='?', help='Recebe o número da empresa a qual deseja adquirir acesso')
args = parser.parse_args()

if args.number is not None:
    api = FetchApi(stone_code=int(args.number), base_url='prod')
else:
    api = FetchApi(base_url='prod', stone_code=85071722)  # company_number="85071722"

api.get_access_token()
api.permit_client(requestType="T", filiates=None)

try:
    path = os.getcwd()
    path += f'/connection/access/company-tokens/token-{api.stone_code}.json'
    with open(path) as f:
        data = json.load(f)
except:
    logger.error("Arquivo com companyNumber e infos inexistente")
    sys.exit()

api.get_status_client(data['requestId'])
