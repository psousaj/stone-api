import locale
import os
import requests
from configs.logging_config import Logger


class FetchAccess:


    def __init__(self, application_key, encryption_string, signature, stone_code, base_url):
        self.logger = Logger(__name__).logger
        self.application_key = application_key
        self.encryption_string = encryption_string
        self.signature = signature
        self.stone_code = stone_code
        self.base_url = base_url

    def create_access(self):
        self.logger.info(f"solicitação de acesso enviada para {self.stone_code}")
        url = f'{self.base_url}/{self.stone_code}/access-authorization'
        headers = {'Authorization': f'Bearer {self.application_key}', 'x-authorization-raw-data': self.encryption_string, 'x-authorization-encrypted-data': self.signature}

        cert_path = os.getcwd()
        cert1 = cert_path + r"\connection\access\ssl\cloudflare.pem"
        cert2 = cert_path + r"\connection\access\ssl\cloudflare_key.pem"
        cert_path = (cert1, cert2)
        # with open(cert_path, 'rb') as f:
        #     cert = f.read()

        response = requests.put(url, headers=headers, cert=cert_path)

        if response.status_code == 202:
            self.logger.info(f"Acesso a {self.stone_code} solicitado com sucesso: {response}")
            self.logger.info("Aguardando resposta do cliente")
        else:
            self.logger.info("--"*20)
            self.logger.error(f'{response} code:{response.status_code}')

    def get_status(self, reference_date):
        url = f'{self.base_url}/{self.stone_code}/access-authorization/status?since={reference_date}'
        headers = {'Authorization': f'Bearer {self.application_key}', 'x-authorization-raw-data': self.encryption_string, 'x-authorization-encrypted-data': self.signature}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            self.logger.info("--"*20)
            response = response.json()
            self.logger.info(response)
            self.logger.info("--"*20)
            self.logger.info(f'Status da solicitação à empresa {self.stone_code}: {response["currentAccessStatus"]}')
        else:
            self.logger.info("--"*20)
            self.logger.error(f'{response.text} {response}')


