import requests
import json
import os
from datetime import datetime
import xml.etree.ElementTree as ET
from connection.access.fetch_access import FetchAccess
from configs.logging_config import logger


class FetchApi:
    path = os.getcwd()
    path += r'\configs\stone-credentials.json'
    with open(path, 'r') as f:
        data = json.load(f)

    def __init__(self, stone_code, date):
        # logging_config.classe = self.__class__.__name__
        self.base_url = 'https://conciliation.stone.com.br/v1/merchant'
        self.date = date
        self.stone_code = stone_code
        # ------
        logger.info("API STONE Inicializada com sucesso")
        logger.info(self.base_url)
        # -- Credenciais
        self.application_key = self.data['ClientApplicationKey']
        self.secret_key = self.data['SecretKey']
        self.encryption_string = self.data['ClientEncryptionString']
        self.signature = self.data['Signature']

    def permit_client(self):
        logger.info(f"solicitando acesso aos dados do cliente: {self.stone_code}")
        api = FetchAccess(self.application_key, self.encryption_string, self.stone_code, self.base_url)
        api.create_access()
        logger.debug("--" * 20)

    def get_status_client(self, reference_date):
        logger.info(f"requisitando status de acesso cliente: {self.stone_code}")
        api = FetchAccess(self.application_key, self.encryption_string, self.stone_code, self.base_url)
        api.get_status(reference_date)

    def get_extrato(self):
        logger.info(f"buscando informações de vendas cliente: {self.stone_code}")
        extrato_url = f'{self.base_url}/{self.stone_code}/conciliation-file/{datetime.strftime(self.date, "%Y%m%d")}'

        headers = {'Authorization': f'Bearer {self.application_key}',
                   'x-authorization-raw-data': self.encryption_string,
                   'x-authorization-encrypted-data': self.signature,
                   'Accept': 'application/xml'}
        response = requests.get(extrato_url, headers=headers)

        if response.status_code == 200:
            root = ET.fromstring(response.content)

            path = os.getcwd()
            path += r'\connection\files\{}\{}\{}-{}\extrato-{}.xml'.format(self.stone_code,
                                                                        datetime.strftime(self.date, '%Y'),
                                                                        datetime.strftime(self.date, '%m'),
                                                                        datetime.strftime(self.date, '%B'),
                                                                        self.date.day)
            replace = '\extrato-{}.xml'.format(self.date.day)
            if not os.path.exists(path.replace(replace, "")):
                os.makedirs(path.replace(replace, ""))
            with open(path, 'w') as file:
                file.write(response.text)

            logger.info(f"Arquivo de extrato baixado com sucesso em:\n{path}")
        else:
            logger.error("Erro interno")
            logger.info('--' * 20)
            logger.error(f'{response.text} {response}')
