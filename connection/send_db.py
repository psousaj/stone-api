from configs import logging_config
from configs.logging_config import logger
from connection.connectdb import Connect
import json


class SendDB:

    def __init__(self, data):
        self.conn = Connect().con
        self.cursor = self.conn.cursor()
        self.data = json.loads(data)
        logging_config.classe = self.__class__.__name__

    def execute(self):
        data = self.data
        cur = self.cursor
        con = self.conn

        for entry in data:
            sql = """INSERT INTO public.rede_api_teste 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            logger.debug(entry)

            cur.execute(sql, (entry['cod_empresa'], entry['DataVenda'], entry['Valor'],
                              entry['TaxaMdr'], entry['ValorMdr'], entry['ValorLiquido'],
                              entry['Modalidade'], entry['Parcelas'], entry['Status'],
                              entry['NSU'], entry['NumeroVenda'], entry['Empresa']))

            con.commit()

        cur.close()
        con.close()
