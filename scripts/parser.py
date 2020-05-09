import requests
from bs4 import BeautifulSoup


def parse_news(params):
    url = 'https://www.audit-it.ru/news/finance/'
    response = requests.get(url).text
    if response:
        soup = BeautifulSoup(response, 'html.parser')
        time_list = soup.find_all('div', {'class': 'comparison-route-snippet-view__route-time-text'})
        return time_list[1].text
    else:
        print('error while getting page, status code: {}'.format(response.status_code))
        return None


print(parse_news(params))

