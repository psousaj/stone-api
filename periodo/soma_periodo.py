from datetime import datetime
import pandas as pd
import locale
# import psycopg2

from configs import logging_config
from configs.logging_config import logger


class RelatorioPeriodo():

    @staticmethod
    def connect_bd(date):
        # path = os.getcwd()
        # path += r'\vendas\files\sumario-vendas-{}.csv'.format(date.strftime('%B'))

        con = psycopg2.connect(host="192.168.1.54", user="postgres",
                               password="1234", database='DataBaseTax')
        df = pd.read_sql("select * from public.rede_api_teste", con=con)
        return df

    @staticmethod
    def get_values(df, actual_date):
        values = 0
        for i, date in enumerate(df['DataVenda']):
            if not pd.isna(date):
                date = datetime.strptime(str(date), '%Y-%m-%d')
                if date.month == actual_date.month:
                    logger.debug("---" * 20)
                    string = f'{date.strftime("%d/%m/%Y")} está dentro do mes de {str(date.strftime("%B")).upper()}'
                    logger.info(string)
                    value = df.iloc[i]['Valor']
                    values += value
                    logger.info(f'Adicionando valor {value}')
                else:
                    logger.error(False)
            else:
                pass
        return values

    @staticmethod
    def perform(value, df, date):
        logger.debug("---" * 20)
        logger.info(f"Relatório {df['Empresa'][1]} - {str(date.strftime('%B')).upper()} ")
        string = 'VALOR TOTAL NO PERIODO: R${:,.2f}'.format(value)
        logger.info(string)

    def __init__(self, start_date):
        logging_config.classe = self.__class__.__name__
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
        self.df = RelatorioPeriodo.connect_bd(start_date)
        self.value = RelatorioPeriodo.get_values(self.df, start_date)
        RelatorioPeriodo.perform(self.value, self.df, start_date)



