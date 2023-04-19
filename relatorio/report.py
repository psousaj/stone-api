from datetime import datetime
import re
import sys
import time
import pandas as pd
from configs.logging_config import Logger
from connection.connectdb import Connect, EmptyDataFrameException
from utils.validate_fee import validate, expected_fee
from configs.validations import save_excel, getPath, find_desktop_path, get_report_path, get_company_db

class RelatorioPeriodo():

    def __init__(self, date:datetime, code, retro = False):
        self.logger = Logger(__name__).logger
        self.DB = Connect()
        self.empresa = self.DB.get_company_name_or_cnpj(code, "name")
        self.cnpj = self.DB.get_company_name_or_cnpj(code, "cnpj")
        try: self.df = self.DB.get_db(get_company_db(self.cnpj, date, retro))
        except EmptyDataFrameException: self.logger.info("Não há registros de vendas referentes ao período desejado"); sys.exit() 
        self.date = date
        self.value = 0
        self.code = code 
        self.retro = retro
        self.report_path = get_report_path()
        self.counter = {'fee_errors': 0, 'not_receivables': 0, 'payments':0, 'sales': 0}

    def get_values(self) -> 'RelatorioPeriodo':
        """Consulta os valores e gera a soma do período informado
        """
        values = 0
        for i, date in enumerate(self.df['DataVenda']):
            date = datetime.strptime(date, "%d/%m/%Y %H:%M").strftime("%d/%m/%Y") if not date is None else datetime(2023, 1, 1)
            self.logger.debug("---" * 10)
            string = f'{date} - {self.empresa}'
            self.logger.info(string)
            value = self.df.iloc[i]['Valor']
            tx_type = self.df.iloc[i]['Modalidade']
            values += value
            self.logger.info('Adicionando venda {}: R${:,.2f}'.format(tx_type, value))
            self.counter['sales'] += 1
        self.value = values
        
        return self
    
    def contabil_report(self):
        df = self.df
        colunas = ['Tipo', 'Data', 'Credito', 'Debito', 'Valor', 'Historico']
        path = getPath(self.code, self.date, "xlsx", 
                       complete=True, create_if_not_exists=True, report_path=True, 
                       company=self.empresa, report_type="02-contabil")
        desktop = find_desktop_path()
        contabil_df = pd.DataFrame(columns=colunas)

        for i, dataVenda in enumerate(df['DataVenda']):
            contabil_df.loc[i, 'Tipo'] = 1
            contabil_df.loc[i, 'Data'] = dataVenda.strftime("%d/%m/%Y")
            contabil_df.loc[i, 'Credito'] = "12345678"
            contabil_df.loc[i, 'Debito'] = "87654321"
            contabil_df.loc[i, 'Valor'] = df.loc[i, 'Valor']
            contabil_df.loc[i, 'Historico'] = f"VENDA {df.loc[i, 'Modalidade']}"
        contabil_df['Data'] = pd.to_datetime(contabil_df['Data']).dt.strftime('%d/%m/%Y')
        contabil_df = contabil_df.sort_values('Data')

        print(contabil_df.head())
        save_excel(contabil_df, path, desktop)
        self.logger.info(f"Relatorio contabil salvo com sucesso em: \n{path}")
        return self

    def show(self):
        date = self.date
        mes = str(date.strftime('%B')).upper() if not self.retro else ''
        self.logger.debug("---" * 10)
        self.logger.info(f"RELATÓRIO {self.empresa} - {mes}")
        string = 'Valor total no período: R${:,.2f}'.format(self.value)
        self.logger.info(string)
        self.logger.info(f"Total de vendas: {self.counter['sales']}")
        self.logger.info(f"Recebimentos vendas: {self.counter['payments']}")
        self.logger.info(f"Erros em taxas: {self.counter['fee_errors']}")
        strf = f"Vendas sem recebimentos: {self.counter['not_receivables']}" if self.counter['not_receivables'] != 0 else "Não há registros referentes à vendas sem recebimentos no período"
        self.logger.info(strf)
        self.logger.debug("-"*20)
        self.logger.info(f"Arquivos salvos em: \n{self.report_path}")

    def cert_fee(self):
        df = self.df
        desktop = find_desktop_path()
        path = getPath(df.loc[0, 'cod_empresa'], self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="04-erros-em-taxas", retro=self.retro)
        path_cert = getPath(df.loc[0, 'cod_empresa'], self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="03-taxas", retro=self.retro)
        colunas = ["Venda", "Valor", "TaxaMdr%", "TaxaEsperada%", "ValorMdr", "ValorLiquido", 
                   "Bandeira", "Modalidade", "Parcelas", "NSU", "CNPJ", "Empresa"]
        error_df = pd.DataFrame(columns=colunas)
        cert_df = pd.DataFrame(columns=colunas)
        cert_df = cert_df.rename(columns={"TaxaEsperada%": "TaxaEncontrada"})

        for i, fee in enumerate(df['TaxaMdr']):
            bandeira = df.loc[i, 'Bandeira']
            time.sleep(0.02)
            isvalid = validate(fee, bandeira)
            self.logger.info(f"{fee} - {isvalid}")

            if not isvalid:
                df['DataVenda'] = pd.to_datetime(df['DataVenda'], format="%d/%m/%Y %H:%M").dt.strftime("%d/%m/%Y %H:%M")
                error = df.iloc[i].tolist()
                self.counter['fee_errors'] += 1

                error_df.loc[i, 'Venda'] = error[2]
                error_df.loc[i, 'Valor'] = error[3]
                error_df.loc[i, 'TaxaMdr%'] = error[4]
                error_df.loc[i, 'TaxaEsperada%'] = expected_fee(fee, bandeira)
                error_df.loc[i, 'ValorMdr'] = error[5]
                error_df.loc[i, 'ValorLiquido'] = error[6]
                error_df.loc[i, 'Bandeira'] = error[12] 
                error_df.loc[i, 'Modalidade'] = error[7]
                error_df.loc[i, 'Parcelas'] = error[9]
                error_df.loc[i, 'NSU'] = error[10]
                error_df.loc[i, 'CNPJ'] = error[13]
                error_df.loc[i, 'Empresa'] = self.empresa
            elif isvalid: 
                # self.logger.debug("ACERTO MIZERAVI")
                df['DataVenda'] = pd.to_datetime(df['DataVenda'], format="%d/%m/%Y %H:%M").dt.strftime("%d/%m/%Y %H:%M")
                cert = df.iloc[i].tolist()

                cert_df.loc[i, 'Venda'] = cert[2]
                cert_df.loc[i, 'Valor'] = cert[3]
                cert_df.loc[i, 'TaxaMdr%'] = cert[4]
                cert_df.loc[i, 'TaxaEncontrada'] = isvalid[2]
                cert_df.loc[i, 'ValorMdr'] = cert[5]
                cert_df.loc[i, 'ValorLiquido'] = cert[6]
                cert_df.loc[i, 'Bandeira'] = cert[12]
                cert_df.loc[i, 'Modalidade'] = cert[7]
                cert_df.loc[i, 'Parcelas'] = cert[9]
                cert_df.loc[i, 'NSU'] = cert[10]
                cert_df.loc[i, 'CNPJ'] = cert[13]
                cert_df.loc[i, 'Empresa'] = self.empresa

        # error_df.loc[len(error_df)+1, 'ValorMdr']

        print(error_df.head())

        save_excel(error_df, path, desktop)
        save_excel(cert_df, path_cert, desktop)
        return self

    def loc_sales_receives(self):
        desktop = find_desktop_path()
        path = getPath(self.empresa, self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="05-recebimentos-vendas", retro=self.retro)
        db = self.DB

        sql = ''
        if self.retro:
            sql = f'''
        SELECT vendas_cartao."NSU", vendas_cartao."DataVenda" as "Venda", public.recebiveis_cartao."DataRecebimento" as "Recebimento", "Valor", 
        vendas_cartao."ValorMdr", recebiveis_cartao."ValorAntecipacao", recebiveis_cartao."ValorLiquido", 
        vendas_cartao."TaxaMdr" as "MDR %", recebiveis_cartao."TaxaAntecipacao" as "Antecipacao %", vendas_cartao."Modalidade", vendas_cartao."Empresa" as "CNPJ"
        FROM public.vendas_cartao 
        JOIN public.recebiveis_cartao ON vendas_cartao."NSU" = recebiveis_cartao."NSU" 
        WHERE recebiveis_cartao."NSU" IS NOT NULL
        AND recebiveis_cartao."DataRecebimento" <= vendas_cartao."DataVenda" + interval '45 days'
        ORDER BY vendas_cartao."DataVenda" ASC
        ''' 
        else: 
            sql = f'''
        SELECT vendas_cartao."NSU", vendas_cartao."DataVenda" as "Venda", public.recebiveis_cartao."DataRecebimento" as "Recebimento", "Valor", 
        vendas_cartao."ValorMdr", recebiveis_cartao."ValorAntecipacao", recebiveis_cartao."ValorLiquido", 
        vendas_cartao."TaxaMdr" as "MDR %", recebiveis_cartao."TaxaAntecipacao" as "Antecipacao %", vendas_cartao."Modalidade", vendas_cartao."Empresa" as "CNPJ"
        FROM public.vendas_cartao 
        JOIN public.recebiveis_cartao ON vendas_cartao."NSU" = recebiveis_cartao."NSU" 
        WHERE recebiveis_cartao."NSU" IS NOT NULL
        AND to_char(vendas_cartao."DataVenda", 'YYYY-MM') = '{self.date.year}-{self.date.strftime("%m")}'
        AND recebiveis_cartao."DataRecebimento" <= vendas_cartao."DataVenda" + interval '45 days'
        ORDER BY "Venda" ASC
        ''' 
        try:  
            df = db.get_db(sql)
            print(df.head())
            df['Venda'] = pd.to_datetime(df['Venda']).dt.strftime('%d/%m/%Y')
            df['Recebimento'] = pd.to_datetime(df['Recebimento']).dt.strftime('%d/%m/%Y')
            df = df.sort_values(by='Venda')
            df['Empresa'] = self.empresa

            save_excel(df, path, desktop)
            self.counter['payments'] = df['Venda'].size
        except Exception as e:
            self.logger.error(f"\n{sql}")
            self.logger.error(f"{e}")
            self.logger.error("Não há registros referentes à vendas recebidas")
            time.sleep(10)

        return self
          
    def loc_sales_without_receives(self):
        ##--Localizar vendas e contar
        self.loc_sales_receives()

        desktop = find_desktop_path()
        path = getPath(self.empresa, self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="06-vendas-sem-recebimentos", retro=self.retro)
        db = self.DB

        sql = ''
        if self.retro:
            sql = f'''
        SELECT vendas_cartao."NSU", vendas_cartao."DataVenda" as "Venda", public.recebiveis_cartao."DataRecebimento" as "Recebimento", "Valor", 
        vendas_cartao."ValorMdr", recebiveis_cartao."ValorAntecipacao", recebiveis_cartao."ValorLiquido", 
        vendas_cartao."TaxaMdr" as "MDR %", recebiveis_cartao."TaxaAntecipacao" as "Antecipacao %", vendas_cartao."Modalidade", vendas_cartao."Empresa" as "CNPJ"
        FROM public.vendas_cartao 
        LEFT JOIN public.recebiveis_cartao on vendas_cartao."NSU" = recebiveis_cartao."NSU" 
        WHERE recebiveis_cartao."NSU" IS NULL
        ORDER BY vendas_cartao."DataVenda" ASC
        ''' 
        else: 
            sql = f'''
        SELECT vendas_cartao."NSU", vendas_cartao."DataVenda" as "Venda", public.recebiveis_cartao."DataRecebimento" as "Recebimento", "Valor",
        vendas_cartao."ValorMdr", recebiveis_cartao."ValorAntecipacao", recebiveis_cartao."ValorLiquido",
        vendas_cartao."TaxaMdr" as "MDR %", recebiveis_cartao."TaxaAntecipacao" as "Antecipacao %", vendas_cartao."Modalidade", vendas_cartao."Empresa" as "CNPJ"
        FROM public.vendas_cartao
        lEFT JOIN public.recebiveis_cartao ON vendas_cartao."NSU" = recebiveis_cartao."NSU"
        WHERE recebiveis_cartao."NSU" IS NULL
        AND to_char(vendas_cartao."DataVenda", 'YYYY-MM') = '{self.date.year}-{self.date.strftime("%m")}'
        ORDER BY vendas_cartao."DataVenda" ASC
        ''' 

        try:
            df = db.get_db(sql)
            print(df.head())
            df['Venda'] = pd.to_datetime(df['Venda']).dt.strftime('%d/%m/%Y')
            df['Recebimento'] = pd.to_datetime(df['Recebimento']).dt.strftime('%d/%m/%Y')
            df = df.sort_values(by='Venda')
            df['Empresa'] = self.empresa

            save_excel(df, path, desktop)
            self.counter['not_receivables'] = df['Venda'].size
        except Exception as e:
            self.logger.error("Não há registros referentes à vendas sem recebimentos no período")

        return self

