import psycopg2
import pandas as pd
import warnings
from psycopg2 import errorcodes
from configs.validations import *
from configs.logging_config import Logger


class EmptyDataFrameException(Exception):
    """Classe para exceção de DataFrame vazio"""
    def __init__(self, message):
        super().__init__(message)


class Connect:
    """Classe para gerenciar a conexão com o banco de dados"""

    logger = Logger(__name__).logger

    def __init__(self, host:str="192.168.1.54", user:str="postgres", password:str="1234", database:str='DataBaseTax'):
        self.con = psycopg2.connect(host=host, user=user, password=password, database=database)
        self.cursor = self.con.cursor()
        warnings.simplefilter("ignore", UserWarning)
        logger.info(f"Conexão com {database} em: {host}")

    def __send_data(self, table_name:str, columns:tuple, *args) -> None:
        """Insere dados no banco de dados e gerencia as exceções"""
        cur = self.cursor
        con = self.con
        placeholders = ", ".join(["%s"] * len(*args))
        lista = tuple(list(*args))
        columns = str(columns).replace('\'', '\"')

        sql = f'''INSERT INTO public.{table_name} {columns} VALUES ({placeholders})'''
        try:
            cur.execute(sql, lista)
            con.commit()
            self.logger.info(f"{lista}")
            self.logger.debug("-" * 10)
        except psycopg2.Error as error:
            if error.pgcode == errorcodes.UNIQUE_VIOLATION:
                logger.info(f"Violação de Constraint, registro já salvo no banco de dados")
                con.rollback()
            else:
                logger.error(f'{error.pgerror}')
                time.sleep(10)

    def send_vendas(self, *args):
        """Insere dados na tabela 'vendas_cartao' do banco de dados"""
        table_name = "vendas_cartao"
        columns = ('Maquineta', 'cod_empresa','DataVenda', 'Valor','TaxaMdr', 'ValorMdr', 
                   'ValorLiquido','Modalidade','Parcelas', 'Status', 'NSU', 'NumeroVenda', 'Bandeira', 'Empresa')
        self.__send_data(table_name, columns, *args)

    def send_recebiveis(self, *args):
        """Insere dados na tabela 'recebiveis_cartao' do banco de dados"""
        table_name = "recebiveis_cartao"
        columns = ('Maquineta', 'cod_empresa','DataRecebimento', 'ValorOriginal','ValorBruto', 'ValorLiquido', 
                   'TaxaMdr','ValorMdr','TaxaAntecipacao', 'ValorAntecipacao', 'NSU', 'Empresa')
        self.__send_data(table_name, columns, *args)

    def get_db(self, sql:str) -> pd.DataFrame:
        """Executa uma consulta SQL e retorna um DataFrame Pandas"""
        con = psycopg2.connect(host="192.168.1.54", user="postgres",
                            password="1234", database='DataBaseTax')
        df = pd.read_sql(f"{sql}", con=con)
        if df.size == 0 or df.size is None:
            raise EmptyDataFrameException("Dataframe vazio, verifique a cláusula SQL")
        return df

    def get_company_name_or_cnpj(self, code:int, info:str):
        return self.execute(info, code=code)

    def execute(self, info:str,  code:int = None, cnpj=None, list=False):
        """execute

        Args:
            info (str): informação desejada (cnpj, operadora, nome da empresa)
            code (int): codigo da maquineta 
            list (bool, optional): informe True se a busca retornar uma lista . Defaults to False.

        Returns:
            tuple: tupla com as informações da query
        """
        where = f'code = {code}' if code is not None else f'cnpj = {cnpj}'   
        sql = f"SELECT {info} FROM public.maquineta_companies WHERE {where}" 
        cur = self.cursor

        try: cur.execute(sql) 
        except TypeError: logger.info(f"Consulta não encontrou nenhum resultado")

        return cur.fetchone()[0] if not list else cur.fetchall()
