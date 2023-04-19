import locale
import calendar
import argparse
from datetime import datetime
from connection.fetch_api import FetchApi

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
code = 740562754 if not args.code else args.code

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
FetchApi(code, date, end_date).permit_client()

