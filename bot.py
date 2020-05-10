import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from requests import get, post, delete

from datetime import datetime
import schedule
import threading
import time
from os import getenv

import yfinance as yf
import pandas as pd

# from config import TOKEN_VK, GROUP_ID
from scripts.functions import *
from scripts.excel_func import create
from scripts.maps import *

# HOST = 'https://api-stocks-kate-daria.herokuapp.com'
HOST = getenv("HOST", "")
TOKEN_VK = getenv("TOKEN_VK", "")
GROUP_ID = getenv("GROUP_ID", "")

users_data = {}
flags = {'AU': '🇦🇺', 'AZ': '🇦🇿', 'GB': '🇬🇧', 'AM': '🇦🇲', 'BY': '🇧🇾', 'BG': '🇧🇬', 'BR': '🇧🇷', 'HU': '🇭🇺',
         'HK': '🇭🇰', 'DK': '🇩🇰', 'US': '🇺🇸', 'EU': '🇪🇺', 'IN': '🇮🇳', 'KZ': '🇰🇿', 'CA': '🇨🇦', 'KG': '🇰🇬',
         'CN': '🇨🇳', 'MD': '🇲🇩', 'NO': '🇳🇴', 'PL': '🇵🇱', 'RO': '🇷🇴', 'SG': '🇸🇬', 'TJ': '🇹🇯', 'TR': '🇹🇷',
         'TM': '🇹🇲', 'UZ': '🇺🇿', 'UA': '🇺🇦', 'CZ': '🇨🇿', 'SE': '🇸🇪', 'CH': '🇨🇭', 'ZA': '🇿🇦', 'KR': '🇰🇷',
         'JP': '🇯🇵'}


class MyErrors(Exception):
    pass


class MessageError(MyErrors):
    pass


class GeoError(MyErrors):
    pass


class DateError(MyErrors):
    pass


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """
    key = input("Enter authentication code: ")
    remember_device = True  # Если: True - сохранить, False - не сохранять.
    return key, remember_device


def generate_keyboard(n):
    global stocks
    keyboard = VkKeyboard(one_time=True)
    if n == 2:
        keyboard.add_button('валюта', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('организации', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('акции', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('помощь', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('рассылка', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Летающие деньги', color=VkKeyboardColor.DEFAULT)
    elif n == 52:
        keyboard.add_button('неделя', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('день', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('вернуться в меню', color=VkKeyboardColor.DEFAULT)
    elif n == 7:
        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
    elif n == 21:
        keyboard.add_button('добавить', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('\U0001F519', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('отписаться от одной', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('отписаться от всех', color=VkKeyboardColor.PRIMARY)
    elif n == 70:
        keyboard.add_button('банк', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('\U0001F519', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('банкомат', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('обмен валюты', color=VkKeyboardColor.PRIMARY)
    elif n == 71:
        keyboard.add_location_button()
        keyboard.add_line()
        keyboard.add_button('вернуться в меню', color=VkKeyboardColor.DEFAULT)
    elif n == 40:
        keyboard.add_button('текущий курс', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('выбрать валюту', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('вернуться в меню', color=VkKeyboardColor.DEFAULT)
    elif n == 42 or n == 31:
        keyboard.add_button('неделя', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('месяц', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('год', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('вернуться в меню', color=VkKeyboardColor.DEFAULT)
    elif n == 30:
        with open('static/static_data/tickers.txt', 'r') as f:
            stocks = f.readlines()[0].split(',')
        for i in range(min(len(stocks), 20)):
            keyboard.add_button(stocks[i], color=VkKeyboardColor.PRIMARY)
            if i % 4 == 3 and i != len(stocks) - 1:
                keyboard.add_line()
    else:
        keyboard.add_button('Вернуться в меню', color=VkKeyboardColor.DEFAULT)
    return keyboard


def new_user(response, vk, uid):
    message = f"Привет, {response[0]['first_name']}!"
    vk.messages.send(user_id=uid,
                     message=message,
                     random_id=get_random_id())
    menu(vk, uid)


def menu(vk, uid):
    users_data[uid]['state'] = 2
    keyboard = generate_keyboard(2)
    vk.messages.send(user_id=uid,
                     message='Добро пожаловать в меню', keyboard=keyboard.get_keyboard(),
                     random_id=get_random_id())


def show_help(response, vk, uid):
    vk.messages.send(user_id=uid, message=f'''\U0001F4DAПомощь\U0001F4DA
Привет, {response[0]['first_name']}
В меню тебя встречает много кнопочек. давай посмотрим, что они умеют:

\U00000031\U000020E3 "Валюта" отвечает за получение различной информации о курсе валют:
\U0001F538 "Текущий курс" покажет тебе список всех валют, которые я знаю, и их текущий курс
\U0001F538 "Выбрать валюту" поможет получить данные о какой-либо валюте за выбранный период. Ты же не против excel? Все, что тебе нужно, - это выбрать валюту (я дам тебе список тех, что знаю, и ты введешь мне номер в списке) и период (например, 01/04/2020-01/05/2020)

\U00000032\U000020E3 "Организации" отыщет ближайшие банки, банкоматы или пункты обмена валют
\U0001F538 выбери тип организации и укажи местоположение

\U00000033\U000020E3 "Акции" поможет получить данные о акциях за выбранный период. аналогично действию "Выбор валюты"

\U00000034\U000020E3 "Рассылка" может сообщить тебе, когда курс какой-либо валюты вырастет или понизится на более чем на р процентов
\U0001F538 "Добавить" начнет добавление новой подписки. Выбери валюту, период, за который нужно смотреть изменение (день или неделя), и сам процент изменения
\U0001F538 "Отписаться от всех" удалит все твои подписки на рассылку
\U0001F538 "Отписаться от одной" покажет список всех твоих подписок с возможностью удаления одной или нескольких из них''',
                     random_id=get_random_id(), keyboard=generate_keyboard(2).get_keyboard())


def choose_currency(vk, uid):
    currency = [str(n + 1) + ' ' + flags.get(item["CharCode"][:2], " ") + f'{item["CharCode"]}' for n, item in
                enumerate(data)]
    vk.messages.send(user_id=uid, message='\U0001F310 Выберите валюту\n' + '\n'.join(currency),
                     random_id=get_random_id(), keyboard=generate_keyboard(0).get_keyboard())
    users_data[uid]['state'] = 41


def check_the_currency_selection(vk, uid, text):
    text = text.rstrip().lstrip()
    try:
        users_data[uid]['currency'] = cur_id[int(text)]
    except Exception:
        raise MessageError
    users_data[uid]['state'] = 42
    vk.messages.send(user_id=uid,
                     message=f'\U0001F4C5 Получите данные за последнюю неделю, месяц, год или введите дату начала и конца периода, за который вы хотите увидеть информацию, в формате dd.mm.YYYY-dd.mm.YYYY',
                     random_id=get_random_id(), keyboard=generate_keyboard(42).get_keyboard())


def check_date_selection(vk, uid, text):
    text = text.lstrip().rstrip().lower()
    d = {'неделя': 7, 'месяц': 30, 'год': 365}
    try:
        if text in d:
            date_to = datetime.date.today().strftime('%d/%m/%Y')
            date_from = (datetime.date.today() - datetime.timedelta(days=d[text])).strftime('%d/%m/%Y')
        else:
            date_from, date_to = text.replace('.', '/').split('-')
        data_of_one_curr = data_of_one_curr_for_a_per(date_from, date_to,
                                                      users_data[uid]['currency'][0])["ValCurs"]["Record"]
        data_of_one_curr = list(map(lambda x: [x["@Date"], float(x["Value"].replace(',', '.'))], data_of_one_curr))
    except Exception:
        raise DateError
    vk.messages.send(user_id=uid, random_id=get_random_id(), message='подождите, собираю информацию\U0001F50E')
    name = from_id_to_name(users_data[uid]['currency'][0])
    code = users_data[uid]['currency'][1]
    filename = f'{code}_{date_from}_{date_to}'.replace('/', '-') + '.xlsx'
    data_ = [{'name': code, 'chart_name': name, 'data': data_of_one_curr}]
    create(data_, filename)
    users_data[uid]['filename'] = filename
    users_data[uid]['count'] = 1


def show_chart(vk, vk_session, uid):
    upload = vk_api.VkUpload(vk_session)
    doc = upload.document_message(f'static/excel/{users_data[uid]["filename"]}', peer_id=uid,
                                  title=users_data[uid]['filename'])['doc']
    attachment = [f'doc{doc["owner_id"]}_{doc["id"]}']
    for i in range(users_data[uid]['count']):
        photo = upload.photo_messages(f'static/img/charts/{users_data[uid]["filename"].split(".")[0]}_{i + 1}.png')[0]
        attachment.append(f'photo{photo["owner_id"]}_{photo["id"]}')
    vk.messages.send(user_id=uid, message='прекрасный выбор', attachment=','.join(attachment),
                     random_id=get_random_id(), keyboard=generate_keyboard(2).get_keyboard())
    users_data[uid]['state'] = 2


def show_all(vk, uid):
    message = [flags.get(item["CharCode"][:2], " ") + f'{item["Nominal"]} {item["CharCode"]}' + f' {item["Value"]} ₽'
               for item in data]
    vk.messages.send(user_id=uid, message='текущий курс\n' + '\n'.join(message),
                     random_id=get_random_id(), keyboard=generate_keyboard(2).get_keyboard())
    users_data[uid]["state"] = 2


def mailing(vk, uid):
    vk.messages.send(user_id=uid, message='управление вашей подпиской \U0001F4B8',
                     random_id=get_random_id(), keyboard=generate_keyboard(21).get_keyboard())
    users_data[uid]['state'] = 50


def mailing_choose(vk, uid):
    message = [str(n + 1) + ' ' + flags.get(item["CharCode"][:2], " ") + f'{item["CharCode"]}' for n, item in
               enumerate(data)]
    vk.messages.send(user_id=uid, message='Об изменении курса какой валюты вам сообщить?\n' + '\n'.join(
        message) + '\nвведите номер валюты в списке',
                     random_id=get_random_id(), keyboard=generate_keyboard(0).get_keyboard())
    users_data[uid]["state"] = 51


def mailing_check_number(vk, uid, text):
    text = text.rstrip().lstrip()
    try:
        users_data[uid]['temporary'] = {}
        users_data[uid]['temporary']['currency'] = cur_id[int(text)]
    except Exception:
        raise MessageError
    vk.messages.send(user_id=uid, message="Изменение за какой период следует отслеживать?",
                     random_id=get_random_id(), keyboard=generate_keyboard(52).get_keyboard())
    users_data[uid]["state"] = 52


def mailing_period(vk, uid, text):
    d = {'день': 1, 'неделя': 7}
    text = text.lstrip().rstrip()
    try:
        users_data[uid]['temporary']['period'] = d[text]
    except Exception:
        raise MessageError
    vk.messages.send(user_id=uid,
                     message="Я сообщу вам, когда курс валюты изменится на р% \n введите р в формате '+р' 📈 или '-р' 📉",
                     random_id=get_random_id(), keyboard=generate_keyboard(0).get_keyboard())
    users_data[uid]["state"] = 53


def mailing_percent(vk, uid, text):
    text = text.lstrip().rstrip()
    try:
        users_data[uid]['temporary']['percent'] = float(text)
    except Exception:
        raise MessageError
    d = {7: 'неделю', 1: 'день'}
    vk.messages.send(user_id=uid,
                     message=f"Я отправлю вам сообщение, если за {d[users_data[uid]['temporary']['period']]} курс " +
                             f"{users_data[uid]['temporary']['currency'][1]} изменится" +
                             f" на {users_data[uid]['temporary']['percent']}%\nВсё правильно?",
                     random_id=get_random_id(), keyboard=generate_keyboard(7).get_keyboard())
    users_data[uid]['state'] = 54


def unsubscribe_from_all(vk, uid):
    res = delete(f'{HOST}/api/user-mailing-lists/{uid}').json()
    if res['success'] == 'OK':
        message = 'вы успешно отписались от всех рассылок'
    else:
        message = 'у вас нет активных подписок'
    vk.messages.send(user_id=uid, message=message,
                     random_id=get_random_id(), keyboard=generate_keyboard(2).get_keyboard())
    users_data[uid]["state"] = 2


def unsubscribe_choose(vk, uid):
    res = get(f'{HOST}/api/user-mailing-lists/{uid}').json()['items']
    if res:
        d = {7: 'week', 1: 'day'}
        users_data[uid]['temporary'] = res
        message = [f'{i + 1} {res[i]["code"]} {d[res[i]["period"]]} {res[i]["percent"]}%' for i in range(len(res))]
        vk.messages.send(user_id=uid, message='Краткая информация о всех ваших подписках:\n' + '\n'.join(
            message) + '\nвведите номера рассылок, от которых хотите отказаться через запятую',
                         random_id=get_random_id(), keyboard=generate_keyboard(0).get_keyboard())
        users_data[uid]["state"] = 60
    else:
        vk.messages.send(user_id=uid, message='у вас нет активных подписок',
                         random_id=get_random_id(), keyboard=generate_keyboard(2).get_keyboard())
        users_data[uid]["state"] = 2


def unsubscribe(vk, uid, text):
    text = text.lstrip().rstrip().split(',')
    items = []
    for item in list(text):
        item = item.rstrip().lstrip()
        if item.isdigit():
            items.append(item)
            try:
                delete(f'{HOST}/api/mailing/{users_data[uid]["temporary"][int(item) - 1]["id"]}').json()
            except Exception:
                pass
    if items:
        vk.messages.send(user_id=uid, message='вы успешно отписаны', random_id=get_random_id())
        menu(vk, uid)
    else:
        raise MessageError


def mailing_add_to_db(vk, uid):
    post(f'{HOST}/api/mailing',
         json={'currency': users_data[uid]['temporary']['currency'][0],
               'period': users_data[uid]['temporary']['period'],
               'uid': uid, 'code': users_data[uid]['temporary']['currency'][1],
               'percent': users_data[uid]['temporary']['percent'],
               'status': True}).json()
    users_data[uid]['temporary'] = {}
    vk.messages.send(user_id=uid, message='подписка успешно активирована', random_id=get_random_id())
    menu(vk, uid)


def flying_money(vk, uid):
    vk.messages.send(user_id=uid, message='Уверены, что хотите летающих денег?',
                     random_id=get_random_id(), keyboard=generate_keyboard(7).get_keyboard())
    users_data[uid]['state'] = 1000


def show_stocks(vk, uid):
    vk.messages.send(user_id=uid,
                     attachment=f'photo-{GROUP_ID}_457239088',
                     random_id=get_random_id(), keyboard=generate_keyboard(30).get_keyboard())
    users_data[uid]["state"] = 30


def stocks_ticker(vk, uid, text):
    text = text.rstrip().lstrip().upper()
    if text not in stocks:
        raise MessageError
    users_data[uid]['temporary'] = {}
    users_data[uid]['temporary']['ticker'] = text
    users_data[uid]['state'] = 31
    vk.messages.send(user_id=uid, keyboard=generate_keyboard(31).get_keyboard(), random_id=get_random_id(),
                     message=f'\U0001F4C5 Получите данные за последнюю неделю, месяц, год или введите дату начала и конца периода, за который вы хотите увидеть информацию, в формате dd.mm.YYYY-dd.mm.YYYY')


def stocks_date(vk, uid, text):
    ticker = users_data[uid]['temporary']['ticker']
    text = text.lstrip().rstrip().lower()
    d = {'неделя': 7, 'месяц': 30, 'год': 365}
    try:
        if text in d:
            date_to = datetime.date.today().strftime('%d/%m/%Y')
            date_from = (datetime.date.today() - datetime.timedelta(days=d[text])).strftime('%d/%m/%Y')
        else:
            date_from, date_to = text.replace('.', '/').split('-')
            datetime.datetime.strptime(date_from, '%d/%m/%Y')
            datetime.datetime.strptime(date_to, '%d/%m/%Y')
        date_from, date_to = map(lambda x: '-'.join(x.split('/')[::-1]), [date_from, date_to])
        vk.messages.send(user_id=uid, random_id=get_random_id(), message='подождите, собираю информацию\U0001F50E')
        data_ = yf.download(ticker, start=date_from, end=date_to).iloc[:, 0:4]
    except Exception as s:
        raise DateError
    open_ = list(zip(*[list(map(lambda x: x.strftime('%d/%m/%Y'), data_.index))] + [data_['Open'].values.tolist()]))
    high = list(zip(*[list(map(lambda x: x.strftime('%d/%m/%Y'), data_.index))] + [data_['High'].values.tolist()]))
    low = list(zip(*[list(map(lambda x: x.strftime('%d/%m/%Y'), data_.index))] + [data_['Low'].values.tolist()]))
    close = list(zip(*[list(map(lambda x: x.strftime('%d/%m/%Y'), data_.index))] + [data_['Close'].values.tolist()]))
    filename = f"{ticker}_{date_from}_{date_to}".replace('/', '-') + '.xlsx'
    data_ = [{'name': ticker, 'chart_name': ticker + ' Open', 'data': open_},
             {'name': ticker, 'chart_name': ticker + ' High', 'data': high},
             {'name': ticker, 'chart_name': ticker + ' Low', 'data': low},
             {'name': ticker, 'chart_name': ticker + ' Close', 'data': close}]
    create(data_, filename=filename)
    users_data[uid]['filename'] = filename
    users_data[uid]['count'] = 4


def type_selection(vk, uid, text):
    text = text.lstrip().rstrip().lower()
    if text not in ['обмен валюты', 'банк', 'банкомат']:
        raise MessageError
    users_data[uid]['type'] = text
    d = {'обмен валюты': 'пункты обмена валют', 'банк': 'банки', 'банкомат': 'банкоматы'}
    vk.messages.send(user_id=uid, random_id=get_random_id(),
                     keyboard=generate_keyboard(71).get_keyboard(),
                     message=f'я найду ближайшие к вам {d[text]}\U0001F4B0 просто выберите ваше местоположение')
    users_data[uid]['state'] = 71


def search_for_banks(vk, vk_session, uid, geo):
    if not geo:
        raise GeoError
    ll = str(geo['coordinates']['longitude']) + ',' + str(geo['coordinates']['latitude'])
    span = "0.003,0.003"
    banks = find_businesses(ll, span, users_data[uid]['type'])
    message = []
    pt = [ll + ',home']
    for i in range(len(banks)):
        pt.append(f'{",".join(list(map(str, banks[i]["geometry"]["coordinates"])))},pm2blm{i + 1}')
        bank = banks[i]["properties"]["CompanyMetaData"]
        message.append('\n'.join(
            [f'{i + 1}. {bank["name"]}', 'Адрес: ' + bank["address"], 'телефон: ' + bank['Phones'][0]["formatted"],
             'режим работы: ' + bank["Hours"]["text"]]))
    if show_map(pt):
        upload = vk_api.VkUpload(vk_session)
        photo = upload.photo_messages('static/img/map.png')[0]
        attachment = f'photo{photo["owner_id"]}_{photo["id"]}'
    else:
        attachment = None
    vk.messages.send(user_id=uid,
                     message='\n\n'.join(message), attachment=attachment,
                     random_id=get_random_id(), dont_parse_links=1)
    menu(vk, uid)


def main():
    vk_session = vk_api.VkApi(token=TOKEN_VK)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            uid = event.message.from_id
            response = vk.users.get(user_id=uid)
            users_data[uid] = users_data.get(uid, dict())
            try:
                if 'state' not in users_data[uid]:
                    new_user(response, vk, uid)
                elif event.message.text.lower() in ['меню', 'вернуться в меню', '\U0001F519']:
                    menu(vk, uid)
                elif users_data[uid]['state'] == 2:
                    if event.message.text.lower() == 'валюта':
                        vk.messages.send(user_id=uid,
                                         message="кнопочки к вашим услугам",
                                         random_id=get_random_id(), keyboard=generate_keyboard(40).get_keyboard())
                        users_data[uid]['state'] = 40
                    elif event.message.text.lower() == 'акции':
                        show_stocks(vk, uid)
                    elif event.message.text.lower() == 'помощь':
                        show_help(response, vk, uid)
                    elif event.message.text.lower() == 'рассылка':
                        mailing(vk, uid)
                    elif event.message.text.lower() == 'летающие деньги':
                        flying_money(vk, uid)
                    elif event.message.text.lower() == 'организации':
                        vk.messages.send(user_id=uid, random_id=get_random_id(),
                                         keyboard=generate_keyboard(70).get_keyboard(),
                                         message='я найду ближайшие к вам банки, банкоматы или пункты обмена валют. Что желаете?')
                        users_data[uid]['state'] = 70
                    else:
                        raise MessageError
                elif users_data[uid]['state'] == 70:
                    type_selection(vk, uid, event.message.text)
                elif users_data[uid]['state'] == 71:
                    search_for_banks(vk, vk_session, uid, event.message.geo)
                elif users_data[uid]['state'] == 30:
                    stocks_ticker(vk, uid, event.message.text)
                elif users_data[uid]['state'] == 31:
                    stocks_date(vk, uid, event.message.text)
                    show_chart(vk, vk_session, uid)
                elif users_data[uid]["state"] == 40:
                    if event.message.text.lower() == 'текущий курс':
                        show_all(vk, uid)
                    elif event.message.text.lower() == 'выбрать валюту':
                        choose_currency(vk, uid)
                    else:
                        raise MessageError
                elif users_data[uid]['state'] == 41:
                    check_the_currency_selection(vk, uid, event.message.text)
                elif users_data[uid]['state'] == 42:
                    check_date_selection(vk, uid, event.message.text)
                    show_chart(vk, vk_session, uid)
                elif users_data[uid]['state'] == 50:
                    if event.message.text.lower() == 'добавить':
                        mailing_choose(vk, uid)
                    elif event.message.text.lower() == 'отписаться от всех':
                        unsubscribe_from_all(vk, uid)
                    elif event.message.text.lower() == 'отписаться от одной':
                        unsubscribe_choose(vk, uid)
                    else:
                        raise MessageError
                elif users_data[uid]['state'] == 51:
                    mailing_check_number(vk, uid, event.message.text)
                elif users_data[uid]['state'] == 52:
                    mailing_period(vk, uid, event.message.text)
                elif users_data[uid]['state'] == 53:
                    mailing_percent(vk, uid, event.message.text)
                elif users_data[uid]['state'] == 54:
                    if 'да' in event.message.text.lower():
                        mailing_add_to_db(vk, uid)
                    else:
                        vk.messages.send(user_id=uid,
                                         message="Тогда попробуем еще раз",
                                         random_id=get_random_id())
                        mailing(vk, uid)
                elif users_data[uid]['state'] == 60:
                    unsubscribe(vk, uid, event.message.text)
                elif users_data[uid]['state'] == 1000:
                    if 'да' in event.message.text.lower():
                        vk.messages.send(user_id=uid, message='Полетели!\n' + '\U0001F4B8' * 1008,
                                         random_id=get_random_id())
                    menu(vk, uid)
                else:
                    raise MessageError
            except DateError:
                keyboard = generate_keyboard(users_data[uid]["state"])
                vk.messages.send(user_id=uid, message='Это не похоже на корректную дату. Попробуй еще раз',
                                 random_id=get_random_id(), keyboard=keyboard.get_keyboard())
            except GeoError:
                vk.messages.send(user_id=uid,
                                 message='Пожалуйста, воспользуйся кнопочкой для выбора местоположения\U0001F5FA\U0001F4CD',
                                 random_id=get_random_id(), keyboard=generate_keyboard(71).get_keyboard())
            except MessageError:
                keyboard = generate_keyboard(users_data[uid]["state"])
                vk.messages.send(user_id=uid, message='Я тебя не понимаю. Попробуй еще раз или вернись в меню',
                                 random_id=get_random_id(), keyboard=keyboard.get_keyboard())
            except Exception as s:
                print(s)
                vk.messages.send(user_id=uid, message='\U000026A0Что-то пошло не так,но мы все исправим\U000026A0',
                                 random_id=get_random_id())
                menu(vk, uid)


def mailing_main():
    list_id_curr = [cur_id[i][0] for i in cur_id]
    week = daily_data_of_all_change(list_id_curr, 7)
    day = daily_data_of_all_change(list_id_curr, 1)
    mailing = {1: day, 7: week}
    all_ = get(f'{HOST}/api/mailing').json()["items"]
    vk_session = vk_api.VkApi(token=TOKEN_VK)
    vk = vk_session.get_api()
    d = {1: 'последний день', 7: "последнюю неделю"}
    for item in all_:
        try:
            if float(mailing[item["period"]][item["currency"]]) >= item["percent"] >= 0:
                message = f"\U00002757 за {d[item['period']]} курс {item['code']} вырос на {mailing[item['period']][item['currency']]}% \U00002757"
                vk.messages.send(user_id=item['uid'], random_id=get_random_id(), message=message)
            elif float(mailing[item["period"]][item["currency"]]) <= item["percent"] <= 0:
                message = f"\U00002757 за {d[item['period']]} курс {item['code']} понизился на {abs(float(mailing[item['period']][item['currency']]))}% \U00002757"
                vk.messages.send(user_id=item['uid'], random_id=get_random_id(), message=message)
        except Exception:
            pass


def load_new_data():
    global data, cur_id
    date = datetime.date.today().strftime('%d/%m/%Y')
    data = daily_data_of_all(date)["ValCurs"]["Valute"]
    cur_id = {i + 1: [data[i]["@ID"], data[i]["CharCode"]] for i in range(len(data))}


def go():
    while True:
        schedule.run_pending()


schedule.every().day.at("06:00").do(load_new_data)
schedule.every().day.at("12:00").do(load_new_data)
schedule.every().day.at("18:00").do(load_new_data)
schedule.every().day.at("12:10").do(mailing_main)

# schedule.every().hour.at(":00").do(mailing_main)
# schedule.every().hour.at(":30").do(mailing_main)
t = threading.Thread(target=go)
t.start()

if __name__ == '__main__':
    load_new_data()
    main()

