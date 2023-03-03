import argparse
import calendar
import locale
from datetime import datetime
import sys
from vendas.sales import SumarioVendas
from connection.connectdb import Connect
from configs.logging_config import logger
from connection.fetch_api import FetchApi
from relatorio.report import RelatorioPeriodo

##--ARGPARSE
parser = argparse.ArgumentParser()
parser.add_argument("--code", nargs='?')
parser.add_argument("--cnpj", nargs='?')
parser.add_argument("--mes", nargs='?')
parser.add_argument("--ano", nargs='?')

args = parser.parse_args()

if args.cnpj is not None:
    DB = Connect()
    sql = f"SELECT cod_maquinetas ->> 'stone' FROM public.companies WHERE cnpj = '{args.cnpj}'"
    result = DB.execute(sql)

##-- SET Initial Configs
date = datetime(2023, 1, 1) if not args.code or not args.cnpj else datetime(args.mes, args.ano, 1)
end_date = date.replace(day=calendar.monthrange(date.year, date.month )[1])
end_date = datetime.now() if not end_date.day > datetime.now().day else end_date
code = 880853854 if not args.code else result

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

sys.exit()
#------------------------------------------------------------------

