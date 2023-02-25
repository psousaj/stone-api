import io
import os
import json
import shutil
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
# from connection.send_db import SendDB
from configs.logging_config import logger
from periodo.soma_periodo import RelatorioPeriodo as relatorio

class SumarioVendas:

    def __init__(self, stone_code, date):
        self.df = None
        self.date = date
        self.stone_code = stone_code
        self.lista = []
        
    def perform(self):
        lista = []
        paste_path = os.getcwd()
        paste_path += r'\connection\files\{}\{}\{}-{}'.format(self.stone_code,
                                                            datetime.strftime(self.date, "%Y"),
                                                            datetime.strftime(self.date, "%m"),
                                                            datetime.strftime(self.date, "%B"))
        if (os.name == "posix"):
            paste_path = paste_path.replace('\\', '/')

        # replace = r'sumario-{}.xlsx'.format(datetime.strftime(self.date, "%B"))
        if not os.path.exists(paste_path):
            os.makedirs(paste_path)
        
        for file in os.listdir(paste_path):
            actual_file = os.path.join(paste_path, file)
            data = self.open_xml_file(actual_file)
            # -- Find Date transaction
            date = datetime.strptime(data.find('Header/ReferenceDate').text, "%Y%m%d")
            date = datetime.strftime(date, "%Y-%m-%d")

            # -- Find CompanyNumber(StoneCode)
            cod = int(data.find('Header/StoneCode').text)

            for item in data.findall('FinancialTransactions/Transaction'):
                valor_liquido = 0.0
                for installment in item.findall('./Installments/Installment'):  # itera as parcelas
                    valor_liquido += float(installment.find('NetAmount').text)  # soma o valor líquido
                valor_liquido = float("{:.2f}".format(valor_liquido))
                valor_bruto = float(item.find('./CapturedAmount').text)
                valor_mdr = float("{:.2f}".format(valor_bruto - valor_liquido))
                taxa_mdr = float("{:.2f}".format((valor_mdr / valor_bruto) * 100))

                modalidade = 'DEBIT' if item.find('./AccountType').text == str(1) else 'CREDIT' if item.find(
                    './AccountType').text == str(2) else 'NOT_CARD_MODALITY'

                info = {
                    'cod_empresa': cod,
                    'DataVenda': date,
                    'Valor': valor_bruto,
                    'TaxaMdr': taxa_mdr,
                    'ValorMdr': valor_mdr,
                    'ValorLiquido': valor_liquido,
                    'Modalidade': modalidade,
                    'Parcelas': item.find('./NumberOfInstallments').text,
                    'Status': 'APPROVED',
                    'NSU': item.find('./AcquirerTransactionKey').text,
                    'NumeroVenda': item.find('./IssuerAuthorizationCode').text,
                    'Empresa': 'Teste',
                }
                lista.append(info)
            self.lista = lista
                
        return lista

    def export(self):
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop') if os.name == "nt" else os.path.join(os.environ['HOME'], 'Área de Trabalho')
        json_df = io.StringIO()
        json.dump(self.lista, json_df)

        # logger.info("Mandando para DataBase")
        # SendDB(json_df.getvalue()).execute()
            
        path = os.getcwd()
        path += r'\vendas\files\{}\{}\sumario-{}.xlsx'.format(self.stone_code, datetime.strftime(self.date, "%Y"), datetime.strftime(self.date, "%B"))
        if (os.name == "posix"):
            path = path.replace('\\', '/')
                                
        replace = r'sumario-{}.xlsx'.format(datetime.strftime(self.date, "%B"))
        if not os.path.exists(path.replace(replace, "")):
            os.makedirs(path.replace(replace, ""))

        df = pd.read_json(json_df.getvalue(), orient="columns")
        df = df.sort_values(by='DataVenda')
        self.df = df
        df.to_excel(path, index=False)
        shutil.copy(path, desktop)

        logger.debug("---" * 20)
        # logger.debug(df.info())
        logger.info(f"Sumario de vendas salvo com sucesso em:\n{path}")
        
    def open_xml_file(self, file_path):
        path = file_path
        data = ET.parse(path).getroot()
        return data

    def getdf(self):
        return self.df