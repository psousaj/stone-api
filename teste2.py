import string
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--primeiro", nargs='?', help="Teste disso aqui")
parser.add_argument("--segundo", nargs='?')

args = parser.parse_args()

print(f"Deu certo - {args.primeiro} - {args.segundo}")
time.sleep(150)