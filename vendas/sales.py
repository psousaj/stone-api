import io
import os
import json
import shutil
import time
import pandas as pd

from datetime import datetime
from connection.connectdb import Connect
from configs.logging_config import logger
from configs.validations import *

class SumarioVendas:

    def __init__(self, code, date):
        sql = f"SELECT name FROM public.companies WHERE cod_maquinetas ->> 'stone' = '{code}'"
        self.date = date
        self.code = code
        self.DB = Connect()
        self.lista = []
        self.lista_excel = []
        self.empresa = self.DB.get_db(sql).loc[0, 'name']
        
    def perform(self) -> 'SumarioVendas':
        lista = []
        lista_excel = []

        dir_path = getPath(self.code, self.date, "xml", create_if_not_exists=True)[0]

        for file in os.listdir(dir_path):
            actual_file = os.path.join(dir_path, file)
            data = load_xml(actual_file)

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
                
        return self

    def export(self):
        json_df = io.StringIO()
        json_db = io.StringIO()
        json.dump(self.lista_excel, json_df)
        json.dump(self.lista, json_db)

        logger.info("Mandando para DataBase")
        self.DB.send(json_db.getvalue())
            
        path = getPath(self.code, self.date, "xlsx", complete=True, create_if_not_exists=True, export_path=True, empresa=self.empresa)

        df = pd.read_json(json_df.getvalue(), orient="columns")
        df = df.sort_values(by='Data da Venda')
        df.loc[0, 'Soma Venda Bruto'] = df['Valor Bruto'].sum()

        desktop_path = find_desktop_path()
        self.__save_file(df, path, desktop_path)

        logger.debug("---" * 20)
        logger.info(f"Relatório de vendas salvo com sucesso em:\n{path}")
        logger.debug("---" * 20)
        
    # def check_anticipation(self, data):
    #     #-- fta = Financial Transactions Accounts
    #     fta = data.findall('./FinancialTransactionsAccounts')
    #     date = datetime.strptime(data.find('Header/ReferenceDate').text, "%Y%m%d")
    #     date = datetime.strftime(date, "%Y-%m-%d")

    #     if not fta: logger.info(f"{} não existem antecipações de vendas nesta data")
        
    def __save_file(self, df:pd.DataFrame, path:str, desktop_path:str):
        while True:
            try:
                df.to_excel(path, index=False)
                shutil.copy(path, desktop_path)
                break
            except PermissionError:
                logger.warning("Erro de Permissão de escrita")
                logger.warning("Por favor feche o arquivo aberto ou veja permissões com o adm do sistema")
                time.sleep(5)