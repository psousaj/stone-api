

import requests

headers = {
  'authorization': 'Basic MDZjMGQxYjItNDY2ZS00MmEwLWIzZTMtMjBhYjJlZDc5MzExOnQ3bnM0NmNoc2k='
}
request = requests.post('https://api.userede.com.br/redelabs/oauth/token/?grant_type=&username=programacao@contabilidade-tax.com.br&password=N-@R%LreSCGJ', headers=headers)

print(request.text)