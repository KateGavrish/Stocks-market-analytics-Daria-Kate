import xmltodict
import json
import requests


def xml_to_json(xml_file):
    my_dict = xmltodict.parse(xml_file)
    json_data = json.loads(json.dumps(my_dict))
    return json_data


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
