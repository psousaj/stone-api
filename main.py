import argparse
from datetime import datetime
import calendar
import locale
from configs.logging_config import logger
from connection.fetch_api import FetchApi
from vendas.sales import SumarioVendas
from relatorio.report import RelatorioPeriodo

##--ARGPARSE
parser = argparse.ArgumentParser()
parser.add_argument("--code", nargs='?')
parser.add_argument("--m", nargs='?')
parser.add_argument("--a", nargs='?')

args = parser.parse_args()

##-- SET Initial Configs
date = datetime(2023, 1, 1) if not args.code else datetime(args.m, args.a, 1)
end_date = date.replace(day=calendar.monthrange(date.year, date.month )[1])
end_date = datetime.now() if not end_date.day > datetime.now().day else end_date
code = 880853854 if not args.code else args.code

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
api = FetchApi(code, date, end_date)
# # -- Busca a API para cada dia do mês
while api.date.month == date.month:
    logger.debug(f'Data Atual: {datetime.strftime(api.date, "%d/%m/%Y")}')
    api.get_extrato()
    api.update_time()

# #-- Envia para o BD e exporta para excel
SumarioVendas(code, date).perform().export()

# #-- Consulta DB e faz o relatório do total de vendas mensal
RelatorioPeriodo(date).perform().show()

#------------------------------------------------------------------

