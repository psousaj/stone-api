import requests
from datetime import datetime, timedelta
from connection.access.fetch_access import FetchAccess
from configs.logging_config import Logger
from configs.validations import *


class FetchApi:
    path = get_config_path()
    data = load_json(path)

    def __init__(self, stone_code, date, end_date):
        self.logger = Logger(__name__).logger
        self.base_url = 'https://conciliation.stone.com.br/v1/merchant'
        self.date = date
        self.stone_code = stone_code
       
        # -- Credenciais
        self.application_key = self.data['ClientApplicationKey']
        self.secret_key = self.data['SecretKey']
        self.encryption_string = self.data['ClientEncryptionString']
        self.signature = self.data['Signature']

         # ------
        self.logger.debug(f'{date.strftime("%d/%m/%Y")} até {end_date.strftime("%d/%m/%Y")}')
        self.logger.info("API STONE Inicializada com sucesso")
        self.logger.info(self.base_url)


    def permit_client(self):
        self.logger.info(f"solicitando acesso aos dados do cliente: {self.stone_code}")

        FetchAccess(self.application_key, self.encryption_string, 
                    self.signature, self.stone_code, 
                    self.base_url).create_access()
        
        self.logger.debug("--" * 20)
        return self

    def get_status_client(self, reference_date=datetime.now().strftime("%Y%m%d")):
        self.logger.info(f"requisitando status de acesso cliente: {self.stone_code}")
        FetchAccess(self.application_key, self.encryption_string, 
                    self.signature, self.stone_code, 
                    self.base_url).get_status(reference_date)

    def get_extrato(self):
        self.logger.info(f"buscando informações de vendas cliente: {self.stone_code}")
        extrato_url = f'{self.base_url}/{self.stone_code}/conciliation-file/{self.date.strftime("%Y%m%d")}'

        headers = {'Authorization': f'Bearer {self.application_key}',
                   'x-authorization-raw-data': self.encryption_string,
                   'x-authorization-encrypted-data': self.signature,
                   'Accept': 'application/xml'}
        response = requests.get(extrato_url, headers=headers)

        if response.status_code == 200:
            path = getPath(self.stone_code, self.date, "xml", complete=True, create_if_not_exists=True)
            
            try:
                save_xml(path, response.text)
            except Exception as e:
                logger.warning("Erro ao salvar")

            self.logger.info(f"Arquivo de extrato baixado em:\n{path}")
        else:
            self.logger.error("Erro interno")
            self.logger.info('--' * 20)
            # logger.error(f'{response.text} {response}')
            self.logger.error(f"{response.status_code}\n{response.text}")

    def update_time(self):
        self.date += timedelta(days=1)