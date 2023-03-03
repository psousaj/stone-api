import argparse
from connection.connectdb import Connect
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--cnpj", nargs='?')
parser.add_argument("--mes", nargs='?')
parser.add_argument("--ano", nargs='?')

args = parser.parse_args()

DB = Connect()
sql = f"SELECT cod_maquinetas ->> 'stone' FROM public.companies WHERE cnpj = '{args.cnpj}'"

result = DB.execute(sql)

print(result)
print(f"Deu certo - {args.cnpj} para {args.mes}/{args.ano}")


# con = Connect.con
# cur = con.cursor()

# sql = f"SELECT name FROM public.companies WHERE cod_maquinetas ->> 'stone' = '{880853854}'"
# empresas = cur.execute(sql)
# empresa = cur.fetchone()[0]

# print("empresa", empresa)
# cur.close()