import locale
import os
import requests
from configs import logging_config
from configs.logging_config import logger


class FetchAccess:

    def __init__(self, application_key, encryption_string, stone_code, base_url):
        logger.info("inicio api de conexão")
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
        self.application_key = application_key
        self.encryption_string = encryption_string
        self.stone_code = stone_code
        self.base_url = base_url
        logging_config.classe = self.__class__.__name__

    def create_access(self):
        logger.info(f"solicitação de acesso enviada para {self.stone_code}")
        url = f'{self.base_url}/{self.stone_code}/access-authorization'
        headers = {'Authorization': f'Bearer {self.application_key}', 'x-authorization-raw-data': self.encryption_string, 'x-authorization-encrypted-data': self.signature}

        cert_path = os.getcwd()
        cert1 = cert_path + r"\connection\access\ssl\cloudflare.pem"
        cert2 = cert_path + r"\connection\access\ssl\cloudflare_key.pem"
        cert_path = (cert1, cert2)
        # with open(cert_path, 'rb') as f:
        #     cert = f.read()

        response = requests.post(url, headers=headers, cert=cert_path)

        if response.status_code == 202:
            logger.info(f"Acesso a {self.stone_code} solicitado com sucesso: {response}")
            logger.info("Aguardando resposta do cliente")
        else:
            logger.info("--"*20)
            logger.error(f'{response.text} code:{response.status_code}')

    def get_status(self, reference_date):
        url = f'{self.base_url}/{self.stone_code}/access-authorization/status?since={reference_date}'
        headers = {'Authorization': f'Bearer {self.application_key}', 'x-authorization-raw-data': self.encryption_string, 'x-authorization-encrypted-data': self.signature}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            logger.info("--"*20)
            response = response.json()
            logger.info(response)
            logger.info("--"*20)
            logger.info(f'Status da solicitação à empresa {self.stone_code}: {response["currentAccessStatus"]}')
        else:
            logger.info("--"*20)
            logger.error(f'{response.text} {response}')


