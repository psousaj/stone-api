from datetime import datetime, timedelta
import calendar
import locale
from connection.fetch_api import FetchApi
from vendas.sales import SumarioVendas
from periodo.soma_periodo import RelatorioPeriodo

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
date = datetime(2023, 2, 7)
month = date.month
end_date = date.replace(day=calendar.monthrange(date.year, month)[1])
stone_code = 880853854

print(datetime.strftime(date, "%d/%m/%Y"))
print(datetime.strftime(end_date, "%d/%m/%Y"))

# #-- Busca a API
# while date.month == month:
api = FetchApi(stone_code=stone_code, date=date)
api.get_extrato()
    # date += timedelta(days=1)
    # print(datetime.strftime(date, "%d/%m/%Y"))

# #-- Envia para o BD e exporta para excel
sumario = SumarioVendas(stone_code, date)
sumario.perform()
sumario.export()


# #-- Consulta DB e faz o relatório do total de vendas mensal
# RelatorioPeriodo(Sdate)

#------------------------------------------------------------------

