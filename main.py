import argparse
import calendar
import locale
from vendas.sales import SumarioVendas
from connection.connectdb import Connect
from datetime import datetime, timedelta
from configs.logging_config import Logger
from connection.fetch_api import FetchApi
from relatorio.report import RelatorioPeriodo

##--ARGPARSE
parser = argparse.ArgumentParser()
parser.add_argument("--code", nargs='?')
parser.add_argument("--cnpj", type=int, nargs='?')
parser.add_argument("--mes", type=int, nargs='?')
parser.add_argument("--ano", type=int, nargs='?')

args = parser.parse_args()

if args.cnpj is not None:
    DB = Connect()
    result = DB.execute(info="cnpj")

##-- SET Initial Configs
date = datetime(2023, 3, 1) if (args.code or args.cnpj is None) else datetime(args.ano, args.mes, 1)
end_date = date.replace(day=calendar.monthrange(date.year, date.month)[1])
end_date = datetime.now() if end_date.day < datetime.now().day else end_date+timedelta(days=5)
code = 880853854 if args.code or args.cnpj is None else result

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
logger = Logger("main_thread").logger
api = FetchApi(code, date, end_date)
#-- Busca a API para cada dia do mês  IMPLEMENTS TIMEDELTA
# while api.date.month == date.month:
#     logger.debug(f'Data Atual: {datetime.strftime(api.date, "%d/%m/%Y")}')
#     api.get_extrato()
#     api.update_time()

# # #-- Envia para o BD e exporta para excel
# SumarioVendas(date, code).get_values().get_receives().fiscal_report()
# # SumarioVendas(date, code).get_values().fiscal_report()
# # SumarioVendas(date, code).get_receives().fiscal_report()

# # #-- Consulta DB e faz o relatório do total de vendas mensal
# (RelatorioPeriodo(date, code).contabil_report()
#                                 .cert_fee()
#                                 .loc_sales_without_receives()
#                                 .get_values()
#                                 .show())

# certFEE
#------------------------------------------------------------------

