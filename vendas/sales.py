import io
import os
import json
import shutil
import time
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from connection.send_db import SendDB
from connection.connectdb import Connect
from configs.logging_config import logger

class SumarioVendas:

    def cursor(self, stone_code):
        sql = f"SELECT name FROM public.companies WHERE cod_maquinetas ->> 'stone' = '{stone_code}'"
        cursor = Connect.con.cursor()
        cursor.execute(sql)
        return cursor

    def __init__(self, stone_code, date):
        self.df = None
        self.date = date
        self.stone_code = stone_code
        self.lista = []
        self.lista_excel = []
        self.empresa = self.cursor(stone_code).fetchone()[0]
        
    def perform(self):
        lista = []
        lista_excel = []
        paste_path = os.getcwd()
        paste_path += r'\connection\files\{}\{}\{}-{}'.format(self.stone_code,
                                                            datetime.strftime(self.date, "%Y"),
                                                            datetime.strftime(self.date, "%m"),
                                                            datetime.strftime(self.date, "%B"))
        if (os.name == "posix"):
            paste_path = paste_path.replace('\\', '/')

        if not os.path.exists(paste_path):
            os.makedirs(paste_path)
        
        for file in os.listdir(paste_path):
            actual_file = os.path.join(paste_path, file)
            data = self.open_xml_file(actual_file)

            #-- Search for changes in sales from previous days
            # self.check_anticipation(data)

            # -- Find Date transaction
            date_time = datetime.strptime(data.find('Header/ReferenceDate').text, "%Y%m%d")
            date = datetime.strftime(date_time, "%Y-%m-%d")
            date_to_excel = datetime.strftime(date_time, "%d/%m/%Y")

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

                modalidade = 'DÉBITO' if item.find('./AccountType').text == str(1) else 'CRÉDITO' if item.find(
                    './AccountType').text == str(2) else 'NOT_CARD_MODALITY'

                db_values = {
                    'cod_empresa': cod,
                    'DataVenda': date,
                    'Valor': valor_bruto,
                    'TaxaMdr': taxa_mdr,
                    'ValorMdr': valor_mdr,
                    'ValorLiquido': valor_liquido,
                    'Modalidade': modalidade,
                    'Parcelas': item.find('./NumberOfInstallments').text,
                    'Status': 'CAPTURED',
                    'NSU': item.find('./AcquirerTransactionKey').text,
                    'NumeroVenda': item.find('./IssuerAuthorizationCode').text,
                    'Empresa': self.empresa,
                }

                info = {
                    'Empresa': self.empresa,
                    'Data da Venda': date_to_excel,
                    'Modalidade': f'{modalidade} {item.find("./NumberOfInstallments").text}x',
                    'Valor Bruto': valor_bruto,
                    'Valor Líquido(Descons. agora)': valor_liquido,
                    'Soma Venda Bruto': None
                }
                lista.append(db_values)
                lista_excel.append(info)

            self.lista = lista
            self.lista_excel = lista_excel
                
        return lista

    def export(self):
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop') if os.name == "nt" else os.path.join(os.environ['HOME'], 'Área de Trabalho')
        json_df = io.StringIO()
        json.dump(self.lista_excel, json_df)

        logger.info("Mandando para DataBase")
        SendDB(json_df.getvalue()).execute()
            
        path = os.getcwd()
        path += r'\vendas\files\{}\{}\relatorio-stone-{}-{}.xlsx'.format(self.empresa, 
                                                              datetime.strftime(self.date, "%Y"), 
                                                              datetime.strftime(self.date, "%B"),
                                                              datetime.strftime(self.date, "%y"))
        if (os.name == "posix"):
            path = path.replace('\\', '/')
                                
        replace = r'relatorio-stone-{}-{}.xlsx'.format(datetime.strftime(self.date, "%B"),
                                                datetime.strftime(self.date, "%y"))
        
        if not os.path.exists(path.replace(replace, "")):
            os.makedirs(path.replace(replace, ""))

        df = pd.read_json(json_df.getvalue(), orient="columns")
        df = df.sort_values(by='Data da Venda')
        df['Soma Venda Bruto'].iloc[0] = df['Valor Bruto'].sum()
        self.df = df

        # #-- Transf to Correct DataTypes
        # datatypes_per_column = {
        #     'Data da Venda': 'datetime64[ms]',
        #         'Modalidade': 'string',
        #         'Valor Bruto': 'float64',
        #         'Valor Líquido(Descons. agora)': 'float64',
        #         'Empresa': 'string',
        #         'Soma Venda Bruto': 'float64'
        # }
        # df.astype(datatypes_per_column)

        while True:
            try:
                df.to_excel(path, index=False)
                shutil.copy(path, desktop)
                break
            except PermissionError:
                logger.warning("Erro de Permissão de escrita")
                logger.warning("Por favor feche o arquivo aberto ou veja permissões com o adm do sistema")
                time.sleep(5)

        logger.debug("---" * 20)
        # logger.debug(df.info())
        logger.info(f"Relatório de vendas salvo com sucesso em:\n{path}")
        
    def open_xml_file(self, file_path):
        path = file_path
        data = ET.parse(path).getroot()
        return data

    def getdf(self):
        return self.df

    # def check_anticipation(self, data):
    #     #-- fta = Financial Transactions Accounts
    #     fta = data.findall('./FinancialTransactionsAccounts')
    #     date = datetime.strptime(data.find('Header/ReferenceDate').text, "%Y%m%d")
    #     date = datetime.strftime(date, "%Y-%m-%d")

    #     if not fta: logger.info(f"{} não existem antecipações de vendas nesta data")
        
        