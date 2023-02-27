import string
import time
import argparse
from connection.connectdb import Connect
from psycopg2.extensions import string_types

parser = argparse.ArgumentParser()
parser.add_argument("--primeiro", nargs='?', help="Teste disso aqui")
parser.add_argument("--segundo", nargs='?')

args = parser.parse_args()

if not args.primeiro:
    print("Sem args")
else:
    print("args")


con = Connect.con
cur = con.cursor()

sql = f"SELECT name FROM public.companies WHERE cod_maquinetas ->> 'stone' = '{880853854}'"
empresas = cur.execute(sql)
empresa = cur.fetchone()[0]

print("empresa", empresa)
cur.close()