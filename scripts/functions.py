import datetime
import xmltodict
import json
import requests


def xml_to_json(xml_file):
    my_dict = xmltodict.parse(xml_file)
    json_data = json.loads(json.dumps(my_dict))
    return json_data


def daily_data_of_all_change(list_id_curr):
    dict_of_delta = dict()
    for id_curr in list_id_curr:
        date1 = datetime.date(2020, 2, 28).strftime('%d/%m/%Y')
        date2 = datetime.date(2020, 3, 28).strftime('%d/%m/%Y')

        a = data_of_one_curr_for_a_per(date1, date2, id_curr)
        try:
            dict_of_delta[id_curr] = str(float(a['ValCurs']['Record'][1]['Value'].replace(',', '.')) * 100 / float(a['ValCurs']['Record'][0]['Value'].replace(',', '.')) - 100)[:5]
        except Exception as e:
            print(e)
            dict_of_delta[id_curr] = 0
    return dict_of_delta


def daily_data_of_all(date):
    """Возвращает данные о валютах на дату в формате dd/mm/yyyy"""

    # print(daily_data_of_all('12/02/2020'))

    date = {'date_req': date}
    return xml_to_json(requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params=date).text)


def data_of_one_curr_for_a_per(date_from, date_to, id_curr):
    """Возвращает данные о валюте на период"""

    # print(data_of_one_curr_for_a_per('12/02/2020', '12/03/2020', 'R01235'))

    data = {'date_req1': date_from, 'date_req2': date_to, 'VAL_NM_RQ': id_curr}
    return xml_to_json(requests.get('http://www.cbr.ru/scripts/XML_dynamic.asp', params=data).text)


def from_id_to_name(id):
    """По id возвращает название"""

    with open('static/static_data/code_of_currency.json') as f:
        score = f.read()
    resp = json.loads(score)
    for i in range(len(resp['Valuta']['Item'])):
        if resp['Valuta']['Item'][i]['@ID'] == id:
            return resp['Valuta']['Item'][i]['Name']
    return


def from_name_to_id(name):
    """По названию возвращает id"""

    with open('static/static_data/code_of_currency.json') as f:
        score = f.read()
    resp = json.loads(score)
    for i in range(len(resp['Valuta']['Item'])):
        if resp['Valuta']['Item'][i]['Name'] == name:
            return resp['Valuta']['Item'][i]['@ID']
    return


def from_code_to_id(code, name=False):
    """По коду возвращает id"""

    with open('static/static_data/code_of_currency_with_iso_char_code.json', 'r', encoding='utf-8-sig') as f:
        resp = json.loads(f.read())
    for i in resp['Valuta']['Item']:
        if i["ISO_Char_Code"] == code:
            if name:
                return i['@ID'], i["Name"]
            else:
                return i['@ID']
    return


def list_of_tuples_id_and_name():
    a = []
    with open('static/static_data/code_of_currency_with_iso_char_code.json', 'r', encoding='utf-8-sig') as f:
        resp = json.loads(f.read())
    for i in resp['Valuta']['Item']:
        a.append((i['@ID'], i["Name"]))

    return a
