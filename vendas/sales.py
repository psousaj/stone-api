import io
import os
import json
import time
import pandas as pd
from datetime import datetime
from connection.connectdb import Connect
from configs.logging_config import Logger
from configs.validations import *
from utils.brand_select import get_brand_name

class SumarioVendas:

    

    def __init__(self, date, code):
        self.date = date
        self.code = code
        self.logger = Logger(__name__).logger
        self.DB = Connect()
        self.lista = []
        self.lista_excel = []
        self.lista_receives = []
        self.empresa = self.DB.get_company_name_or_cnpj(code, "name")
        self.cnpj = self.DB.get_company_name_or_cnpj(code, "cnpj")
        
    def get_values(self) -> 'SumarioVendas':
        lista = []
        lista_excel = []

        dir_path = getPath(self.code, self.date, "xml", create_if_not_exists=True)[0]
        for file in os.listdir(dir_path):
            actual_file = os.path.join(dir_path, file)
            data = load_xml(actual_file)
            #-- Search for changes in sales from previous days
            # self.check_anticipation(data)

            # -- Find CompanyNumber(StoneCode)
            cod = int(data.find('Header/StoneCode').text)
            for item in data.findall('FinancialTransactions/Transaction'):
                # -- Find Date transaction
                date_time = datetime.strptime(item.find('./AuthorizationDateTime').text, "%Y%m%d%H%M%S")
                date = datetime.strftime(date_time, "%Y-%m-%d")
                date_to_excel = datetime.strftime(date_time, "%d/%m/%Y")

                bandeira = get_brand_name(item.find('./BrandId').text)

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
                    'Maquineta': 1,
                    'cod_empresa': cod,
                    'DataVenda': date,
                    'Valor': valor_bruto,
                    'TaxaMdr': taxa_mdr,
                    'ValorMdr': valor_mdr,
                    'ValorLiquido': valor_liquido,
                    'Modalidade': modalidade,
                    'Parcelas': item.find('./NumberOfInstallments').text,
                    'Status': 'APROVADO',
                    'NSU': item.find('./AcquirerTransactionKey').text,
                    'NumeroVenda': item.find('./IssuerAuthorizationCode').text,
                    'Bandeira': bandeira,
                    'Empresa': self.cnpj,
                }

                info = {
                    'Empresa': self.empresa,
                    'Data da Venda': date_to_excel,
                    'Modalidade': f'{modalidade} {item.find("./NumberOfInstallments").text}x',
                    'Valor Bruto': valor_bruto,
                    'Valor Líquido': valor_liquido,
                    # 'Soma Venda Bruto': None
                }
                lista.append(db_values)
                lista_excel.append(info)

            self.lista = lista
            self.lista_excel = lista_excel
                
        return self

    def get_receives(self) -> 'SumarioVendas':
        lista_receives = []

        dir_path = getPath(self.code, self.date, "xml", create_if_not_exists=True)[0]
        for file in os.listdir(dir_path):
            actual_file = os.path.join(dir_path, file)
            data = load_xml(actual_file)
            #-- Search for changes in sales from previous days
            # self.check_anticipation(data)
            # -- Find CompanyNumber(StoneCode)
            cod = int(data.find('Header/StoneCode').text)
            
            for item in data.findall('FinancialTransactionsAccounts/Transaction'):
                valor_liquido = valor_bruto = valor_mdr = valor_antecipacao = taxa_mdr = taxa_antecipacao = 0.0
                nsu = item.find('./AcquirerTransactionKey').text
                for installment in item.findall('./Installments/Installment'):  # itera as parcelas
                    has_installment = installment.find('AdvanceRateAmount')
                    date = datetime.strptime(installment.find('PaymentDate').text, "%Y%m%d").strftime("%d/%m/%Y")
                    valor_liquido += float(installment.find('./NetAmount').text)  # soma o valor líquido
                    valor_bruto += float(installment.find('GrossAmount').text)
                    valor_antecipacao += float(has_installment.text) if has_installment is not None else 0.0

                valor_liquido = self.format_float(valor_liquido)
                valor_bruto = self.format_float(valor_bruto)
                valor_mdr = self.format_float(valor_bruto - valor_liquido)
                taxa_mdr = self.format_float((valor_mdr / valor_bruto) * 100)
                valor_antecipacao = self.format_float(valor_antecipacao)
                taxa_antecipacao = self.format_float((valor_antecipacao / valor_bruto)*100)

                db_values = {
                    'Maquineta': 1,
                    'cod_empresa': cod,
                    'DataRecebimento': date,
                    'ValorOriginal': valor_bruto,
                    'ValorBruto': valor_bruto,
                    'ValorLiquido': valor_liquido,
                    'TaxaMdr': taxa_mdr,
                    'ValorMdr': valor_mdr,
                    'TaxaAntecipacao': taxa_antecipacao,
                    'ValorAntecipacao': valor_antecipacao,
                    'NSU': nsu,
                    'Empresa': self.cnpj,
                }
                lista_receives.append(db_values)

            self.lista_receives = lista_receives
                
        json_receives = json_in_memory(self.lista_receives)
        data = loads_json(json_receives)
        self.logger.info("Enviando recebiveis para DataBase")
        for entry in data:
            values = [1, entry['cod_empresa'], entry['DataRecebimento'], entry['ValorOriginal'], entry['ValorBruto'], 
                        entry['ValorLiquido'], entry['TaxaMdr'], entry['ValorMdr'], entry['TaxaAntecipacao'], 
                        entry['ValorAntecipacao'], entry['NSU'], entry['Empresa']]
            self.DB.send_recebiveis(values)

        return self

    def fiscal_report(self):
        json_df = json_in_memory(self.lista_excel)
        json_db = json_in_memory(self.lista)
        data = loads_json(json_db)
        self.logger.info("Enviando vendas para DataBase")
        for entry in data:
            values = [1, entry['cod_empresa'], entry['DataVenda'], entry['Valor'],
                              entry['TaxaMdr'], entry['ValorMdr'], entry['ValorLiquido'],
                              entry['Modalidade'], entry['Parcelas'], entry['Status'],
                              entry['NSU'], entry['NumeroVenda'], entry['Bandeira'], entry['Empresa']]
            self.DB.send_vendas(values)
            
        path = getPath(self.code, self.date, "xlsx", complete=True, create_if_not_exists=True, 
                       report_path=True, company=self.empresa, report_type="01-fiscal")
        desktop = find_desktop_path()

        df = pd.read_json(json_df, orient="columns")
        df = df.sort_values(by='Data da Venda')
        df = df.assign(**{'Soma Venda Bruto': df['Valor Bruto'].sum()})
        df = df.assign(**{'Soma Liquida': df['Valor Líquido'].sum()})
        df = df.assign(**{'Valor Taxas': df['Valor Bruto'].sum() - df['Valor Líquido'].sum()})
        df.iloc[1:, df.columns.get_loc('Soma Venda Bruto')] = None
        df.iloc[1:, df.columns.get_loc('Soma Liquida')] = None
        df.iloc[1:, df.columns.get_loc('Valor Taxas')] = None

        save_excel(df, path, desktop)

        self.logger.debug("---" * 20)
        self.logger.info(f"Relatório de vendas salvo com sucesso em:\n{path}")
        self.logger.debug("---" * 20)

    def format_float(self, valor:float):
         return float("{:.2f}".format(valor))
    # def check_anticipation(self, data):
    #     #-- fta = Financial Transactions Accounts
    #     fta = data.findall('./FinancialTransactionsAccounts')
    #     date = datetime.strptime(data.find('Header/ReferenceDate').text, "%Y%m%d")
    #     date = datetime.strftime(date, "%Y-%m-%d")

    #     if not fta: logger.info(f"{} não existem antecipações de vendas nesta data")
        