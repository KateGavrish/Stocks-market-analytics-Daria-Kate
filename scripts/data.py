import requests
from functions import xml_to_json


def daily_data_of_all(date):
    """Возвращает """
    return requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params=date)