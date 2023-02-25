from datetime import datetime, timedelta
import calendar
import locale
from configs.logging_config import logger
from connection.fetch_api import FetchApi
from vendas.sales import SumarioVendas
from periodo.soma_periodo import RelatorioPeriodo

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
date = datetime(2022, 6, 1)
month = date.month
end_date = date.replace(day=calendar.monthrange(date.year, month)[1])
stone_code = 880853854

logger.debug(f'{datetime.strftime(date, "%d/%m/%Y")} até {datetime.strftime(end_date, "%d/%m/%Y")}')

api = FetchApi(stone_code=stone_code, date=date)

# # #-- Busca a API
while api.date.month == month:
    logger.debug(f'Data Atual: {datetime.strftime(api.date, "%d/%m/%Y")}')
    api.get_extrato()
    api.update_time()
    

# #-- Envia para o BD e exporta para excel
sumario = SumarioVendas(stone_code, date)
sumario.perform()
sumario.export()


# #-- Consulta DB e faz o relatório do total de vendas mensal
RelatorioPeriodo(sumario.getdf(), date)

#------------------------------------------------------------------

