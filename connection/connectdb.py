import psycopg2
import pandas as pd
import warnings
from configs.validations import *
from configs.logging_config import logger


class Connect:

    def __init__(self):
        host = "192.168.1.54"
        user = "postgres"
        password = "1234"
        database = 'DataBaseTax'
        self.con = psycopg2.connect(host=host, user=user,
                            password=password, database=database)
        self.cursor = self.con.cursor()
        warnings.simplefilter("ignore", UserWarning)
        logger.info(f"Conexão com {database} em: {host}")

    def send(self, data):
        """Envia os dados informados por parâmetro para o banco de dados

        Args:
           - data (str): Dados do json passado em String
        """        
        cur = self.cursor
        con = self.con
        
        data = json.loads(data)
        for entry in data:
            sql = """INSERT INTO public.stone_api 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            try:
                cur.execute(sql, (entry['cod_empresa'], entry['DataVenda'], entry['Valor'],
                              entry['TaxaMdr'], entry['ValorMdr'], entry['ValorLiquido'],
                              entry['Modalidade'], entry['Parcelas'], entry['Status'],
                              entry['NSU'], entry['NumeroVenda'], entry['Empresa']))

                con.commit()
            except Exception:
                logger.info(f"Violação de Constraint, registro já salvo no banco de dados")
        cur.close()
        con.close()

    def execute(self, sql):
        cursor = self.cursor

        cursor.execute(sql)

        result = cursor.fetchone()[0]
        return result

    def get_db(self, sql):
        """Busca os registros referentes ao código do cliente e ao mês informado

        Args:
           - sql (str): Consulta sql em formato de string

        Returns:
           - {df.DataFrame}: Retorna um DataFrame Pandas
        """
        con = psycopg2.connect(host="192.168.1.54", user="postgres",
                               password="1234", database='DataBaseTax')
        df = pd.read_sql(f"{sql}", con=con)
        return df