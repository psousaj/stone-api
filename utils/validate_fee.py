import json
import math    

fee = {'VISA': {'CREDITO':2.7, '12x':3.26, 'DEBITO':1.51}, #, '6x':2.93 
       'MASTER': {'CREDITO':2.7, '12x':3.26, 'DEBITO':1.51},
       'ELO': {'CREDITO':2.93, '12x':3.8, 'DEBITO':1.76}, # , '6x':3.26,
       'AMEX': {'CREDITO':2.42, '6x':2.98, '12x':3.38},
       'HIPERCARD': {'CREDITO':2.17, '6x':3.28, '12x':3.56}}

data = json.dumps(fee)
data = json.loads(data)

def validate(tax:float, brand:str):
    # for brand in data:
    data_brand = data[brand]
    for fee in data_brand:
        comparator = data_brand[fee]
        if math.isclose(tax, comparator, rel_tol=0.00, abs_tol=0.05):
            return (True, str(f'{brand} {fee}'), str(f'{comparator}'))
    return False

def expected_fee(tax:float, brand:str):
    # for brand in data:
    data_brand = data[brand]
    for fee in data_brand:
        comparator = data_brand[fee]
        if math.isclose(tax, comparator, rel_tol=0.00, abs_tol=1):
        # if tax > (comparator+1.6) or tax:
            return str(f'{comparator}%, {brand} {fee}')
    return "Nenhuma taxa aproximada"      

# valor = 2.7
# valid = validate(valor, 'MASTER')
# print(valid[1])
# print(expected_fee(valor, 'ELO'))

# print(0.88 < 0.90)
# print(1.9019019019019 < 1.9)

