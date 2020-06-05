import requests
from os import getenv

API_KEY = getenv("API_KEY", "")


def find_businesses(ll, spn, request, locale="ru_RU"):
    """получение организаций"""
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = API_KEY
    search_params = {
        "apikey": api_key,
        "text": request,
        "lang": locale,
        "ll": ll,
        "spn": spn,
        "type": "biz",
        "results": 5
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(
                request=search_api_server, status=response.status_code, reason=response.reason))

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем организации
    organizations = json_response["features"]
    return organizations


def show_map(pt):
    """создание изображения карты"""
    map_params = {
        "l": "map",
        'pt': '~'.join(pt)
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    if not response:
        print("Ошибка выполнения запроса:")
        print(response.url)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return False
    # Записывание полученного изображения в файл.
    map_file = "static/img/map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        return False
    return True
