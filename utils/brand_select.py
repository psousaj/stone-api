brands = {
    '1': 'VISA',
    '2': 'MASTER',
    '3': 'AMEX',
    '9': 'HIPER',
    '171': 'ELO',
    }

def get_brand_name(brand_id:str) -> str:
    return brands.get(str(brand_id), "Invalid brand_id")
