import psycopg2

from configs import logging_config
from configs.logging_config import logger


class Connect():

    def __init__(self):
        logging_config.classe = self.__class__.__name__

    """
    classe de conexão com o banco de dados postgres 
    """
    host = "192.168.1.54"
    user = "postgres"
    password = "1234"
    database = 'DataBaseTax'
    con = psycopg2.connect(host=host, user=user,
                           password=password, database=database)

    logger.info(f"Conexão com {database} em: {host}")
