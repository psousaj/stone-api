from datetime import datetime
import pandas as pd
from configs.logging_config import logger
from connection.connectdb import Connect


class RelatorioPeriodo():

    def __init__(self, date:datetime):
        self.DB = Connect()
        sql = f'SELECT * FROM public.stone_api WHERE EXTRACT(MONTH FROM "DataVenda") = {date.month}'
        self.df = self.DB.get_db(sql)
        self.date = date
        self.value = 0

    def perform(self) -> 'RelatorioPeriodo':
        """Consulta os valores e gera a soma do período informado
        """
        values = 0
        for i, date in enumerate(self.df['DataVenda']):
            date = date.strftime("%d/%m/%Y") if not date is None else datetime(2023, 1, 1)
            logger.debug("---" * 10)
            string = f'{date} - {self.df.iloc[i]["Empresa"]}'
            logger.info(string)
            value = self.df.iloc[i]['Valor']
            tx_type = self.df.iloc[i]['Modalidade']
            values += value
            logger.info('Adicionando venda {}: R${:,.2f}'.format(tx_type, value))
        self.value = values
        return self
    
    def show(self):
        date = self.df['DataVenda'].iloc[0]
        logger.debug("---" * 10)
        logger.info(f"Relatório {self.df['Empresa'].iloc[0]} - {str(date.strftime('%B')).upper()} ")
        string = 'VALOR TOTAL NO PERIODO: R${:,.2f}'.format(self.value)
        logger.info(string)



