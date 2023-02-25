from datetime import datetime
import pandas as pd
import locale
# import psycopg2
from configs import logging_config
from configs.logging_config import logger


class RelatorioPeriodo():

    # @staticmethod
    # def connect_bd(date):
    #     con = psycopg2.connect(host="192.168.1.54", user="postgres",
    #                            password="1234", database='DataBaseTax')
    #     df = pd.read_sql("select * from public.rede_api_teste", con=con)
    #     return df

    @staticmethod
    def get_values(df, date_time):
        values = 0
        for i, date in enumerate(df['DataVenda']):
            # if not pd.isna(date):
            #     date = datetime.strptime(str(date), '%Y-%m-%d')
            logger.debug("---" * 20)
            # string = f'{date_time.strftime("%d/%m/%Y")} está dentro do mes de {str(date.strftime("%B")).upper()}'
            string = f'{date_time.strftime("%d/%m/%Y")} - NomeEmpresa - {str(date_time.strftime("%B")).upper()}'
            logger.info(string)
            value = df.iloc[i]['Valor']
            tx_type = df.iloc[i]['Modalidade']
            values += value
            logger.info('Adicionando venda {}: R${:,.2f}'.format(tx_type, value))
        return values

    @staticmethod
    def show(value, df=None, date=None):
        logger.debug("---" * 20)
        # logger.info(f"Relatório {df['Empresa'][1]} - {str(date.strftime('%B')).upper()} ")
        string = 'VALOR TOTAL NO PERIODO: R${:,.2f}'.format(value)
        logger.info(string)

    def __init__(self, df, date:datetime):
        # self.df = RelatorioPeriodo.connect_bd(start_date)
        value = RelatorioPeriodo.get_values(df, date)
        RelatorioPeriodo.show(value) #, df, start_date



