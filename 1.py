import json

with open('static/static_data/code_of_currency.json') as f:
    score = f.read()

resp = json.loads(score)
for i in range(len(resp['Valuta']['Item'])):
    print(resp['Valuta']['Item'][i]['@ID'])