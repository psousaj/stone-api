from datetime import datetime
import pandas as pd
import psycopg2
from configs.logging_config import logger


class RelatorioPeriodo():

    # @staticmethod
    # def connect_bd():
    #     con = psycopg2.connect(host="192.168.1.54", user="postgres",
    #                            password="1234", database='DataBaseTax')
    #     df = pd.read_sql("select * from public.stone_api", con=con)
    #     return df

    @staticmethod
    def get_values(df):
        values = 0
        for i, date in enumerate(df['Data da Venda']):
            # date = datetime.strftime(date, "%d/%m/%Y")
            logger.debug("---" * 20)
            string = f'{date} - {df.iloc[i]["Empresa"]}'
            logger.info(string)
            value = df.iloc[i]['Valor Bruto']
            tx_type = df.iloc[i]['Modalidade']
            values += value
            logger.info('Adicionando venda {}: R${:,.2f}'.format(tx_type, value))
        return values

    @staticmethod
    def show(value, df=None):
        date = datetime.strptime(df['Data da Venda'][1], "%d/%m/%Y")
        logger.debug("---" * 20)
        logger.info(f"Relatório {df['Empresa'][1]} - {str(date.strftime('%B')).upper()} ")
        string = 'VALOR TOTAL NO PERIODO: R${:,.2f}'.format(value)
        logger.info(string)

    def __init__(self, df:pd.DataFrame):
        # df = RelatorioPeriodo.connect_bd()
        value = RelatorioPeriodo.get_values(df)
        RelatorioPeriodo.show(value, df=df)



