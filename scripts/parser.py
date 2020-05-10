import requests
from bs4 import BeautifulSoup


def parse_news():
    url = 'https://www.audit-it.ru/news/finance/'
    response = requests.get(url).text
    if response:
        soup = BeautifulSoup(response, 'html.parser')
        time_list = soup.find('ul', {'class': 'type-first info-box'})
        li = time_list.find_all('li')
        return [{'time': l.div.span.text,
                 'title': l.find('div', {'class': "news-title-box"}).a.text,
                 'link': 'https://www.audit-it.ru' + l.find('div', {'class': "news-title-box"}).a['href'],
                 'content': l.find('span', {'class': 'text'}).text}
                for l in li]
    else:
        print('error while getting page, status code: {}'.format(response.status_code))
        return None



