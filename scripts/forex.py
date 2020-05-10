import urllib.request
import urllib.error
import urllib.parse

try:
    import simplejson as json
except ImportError:
    import json

URL_LATEST = 'http://openexchangerates.org/api/latest.json'
URL_HISTORICAL = 'http://openexchangerates.org/api/historical/{0}.json'


def first_to_second(date, base_curr, new_curr, amount):
    request_data = {'app_id': '28d883ed3acb4bb28d22d9c5af20d0fb'}
    url = URL_HISTORICAL.format(date)
    forex_data = get_json(url, request_data)
    conv_rate = forex_data['rates'][new_curr] / forex_data['rates'][base_curr]
    result = amount * conv_rate
    return float("{0:.3f}".format(result))


def get_json(url, data):
    data = urllib.parse.urlencode(data)
    try:
        html = urllib.request.urlopen('{0}?{1}'.format(url, data))
    except urllib.error.URLError as e:
        raise Exception("{0} for {1}".format(e, url))
    except urllib.error as e:
        raise Exception("{0} for {1}".format(e, url))
    raw_json = html.read().decode('utf-8')
    forex_json = json.loads(raw_json)
    return forex_json
