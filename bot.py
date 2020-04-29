import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from requests import get, post, delete

from datetime import datetime
import schedule
import threading
import time

from config import TOKEN_VK, GROUP_ID
from scripts.functions import *
from scripts.excel_func import create_excel_chart

HOST = 'http://127.0.0.1:5000'

users_data = {}
flags = {'AU': '🇦🇺', 'AZ': '🇦🇿', 'GB': '🇬🇧', 'AM': '🇦🇲', 'BY': '🇧🇾', 'BG': '🇧🇬', 'BR': '🇧🇷', 'HU': '🇭🇺',
         'HK': '🇭🇰', 'DK': '🇩🇰', 'US': '🇺🇸', 'EU': '🇪🇺', 'IN': '🇮🇳', 'KZ': '🇰🇿', 'CA': '🇨🇦', 'KG': '🇰🇬',
         'CN': '🇨🇳', 'MD': '🇲🇩', 'NO': '🇳🇴', 'PL': '🇵🇱', 'RO': '🇷🇴', 'SG': '🇸🇬', 'TJ': '🇹🇯', 'TR': '🇹🇷',
         'TM': '🇹🇲', 'UZ': '🇺🇿', 'UA': '🇺🇦', 'CZ': '🇨🇿', 'SE': '🇸🇪', 'CH': '🇨🇭', 'ZA': '🇿🇦', 'KR': '🇰🇷',
         'JP': '🇯🇵'}


class MessageError(Exception):
    pass


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """
    key = input("Enter authentication code: ")
    remember_device = True  # Если: True - сохранить, False - не сохранять.
    return key, remember_device


def generate_keyboard(n):
    keyboard = VkKeyboard(one_time=True)
    if n == 2:
        keyboard.add_button('текущий курс', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('выбрать валюту', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('помощь', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('рассылка', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Летающие деньги', color=VkKeyboardColor.DEFAULT)
    elif n == 5:
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
        keyboard.add_button('🔙', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('отписаться от одной', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('отписаться от всех', color=VkKeyboardColor.PRIMARY)
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


def show_help(vk, uid):
    vk.messages.send(user_id=uid, message='Здесь должна быть помощь',
                     random_id=get_random_id(), keyboard=generate_keyboard(2).get_keyboard())


def choose_currency(vk, uid):
    currency = [str(n + 1) + ' ' + flags.get(item["CharCode"][:2], " ") + f'{item["CharCode"]}' for n, item in
                enumerate(data)]
    vk.messages.send(user_id=uid, message='Выберите валюту\n' + '\n'.join(currency),
                     random_id=get_random_id())
    users_data[uid]['state'] = 3


def check_the_currency_selection(vk, uid, text):
    text = text.rstrip().lstrip()
    try:
        users_data[uid]['currency'] = cur_id[int(text)]
    except Exception:
        raise MessageError
    users_data[uid]['state'] = 4
    vk.messages.send(user_id=uid,
                     message=f'Введите дату начала и конца периода, за который вы хотите увидеть информацию, в формате dd/mm/YY-dd/mm/YY',
                     random_id=get_random_id())


def check_date_selection(vk, uid, text):
    try:
        date_from, date_to = text.split('-')
        data_of_one_curr = data_of_one_curr_for_a_per(date_from, date_to,
                                                      users_data[uid]['currency'][0])["ValCurs"]["Record"]
        data_of_one_curr = list(map(lambda x: [x["@Date"], float(x["Value"].replace(',', '.'))], data_of_one_curr))
    except Exception as s:
        print(s)
        raise MessageError
    name = from_id_to_name(users_data[uid]['currency'][0])
    code = users_data[uid]['currency'][1]
    filename = f'{code}_{date_from}_{date_to}'.replace('/', '-') + '.xlsx'
    create_excel_chart(name, code, data_of_one_curr, filename)
    users_data[uid]['filename'] = filename


def show_chart(vk, vk_session, uid):
    upload = vk_api.VkUpload(vk_session)
    doc = upload.document_message(f'static/excel/{users_data[uid]["filename"]}', peer_id=uid,
                                  title=users_data[uid]['filename'])['doc']
    vk.messages.send(user_id=uid, message='прекрасный выбор', attachment=f'doc{doc["owner_id"]}_{doc["id"]}',
                     random_id=get_random_id(), keyboard=generate_keyboard(2).get_keyboard())
    users_data[uid]['state'] = 2


def show_all(vk, uid):
    message = [flags.get(item["CharCode"][:2], " ") + f'{item["Nominal"]} {item["CharCode"]}' + f' {item["Value"]} ₽'
               for item in data]
    vk.messages.send(user_id=uid, message='текущий курс\n' + '\n'.join(message),
                     random_id=get_random_id(), keyboard=generate_keyboard(2).get_keyboard())


def mailing(vk, uid):
    vk.messages.send(user_id=uid, message='управление вашей подпиской 💸',
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
                     random_id=get_random_id(), keyboard=generate_keyboard(5).get_keyboard())
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
                elif event.message.text.lower() in ['меню', 'вернуться в меню', '🔙']:
                    menu(vk, uid)
                elif users_data[uid]['state'] == 2:
                    if event.message.text.lower() == 'текущий курс':
                        show_all(vk, uid)
                    elif event.message.text.lower() == 'выбрать валюту':
                        choose_currency(vk, uid)
                    elif event.message.text.lower() == 'помощь':
                        show_help(vk, uid)
                    elif event.message.text.lower() == 'рассылка':
                        mailing(vk, uid)
                    elif event.message.text.lower() == 'летающие деньги':
                        flying_money(vk, uid)
                    else:
                        raise MessageError
                elif users_data[uid]['state'] == 3:
                    check_the_currency_selection(vk, uid, event.message.text)
                elif users_data[uid]['state'] == 4:
                    check_date_selection(vk, uid, event.message.text)
                    show_chart(vk, vk_session, uid)
                elif users_data[uid]['state'] == 50:
                    if event.message.text.lower() == 'добавить':
                        mailing_choose(vk, uid)
                    elif event.message.text.lower() == 'отписаться от всех':
                        unsubscribe_from_all(vk, uid)
                    elif event.message.text.lower() == 'отписаться от одной':
                        unsubscribe_choose(vk, uid)
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
                        vk.messages.send(user_id=uid, message='Полетели!\n' + '💸' * 1008,
                                         random_id=get_random_id())
                    menu(vk, uid)
                else:
                    raise MessageError
            except MessageError:
                keyboard = generate_keyboard(users_data[uid])
                vk.messages.send(user_id=uid, message='Я тебя не понимаю. Попробуй еще раз или вернись в меню',
                                 random_id=get_random_id(), keyboard=keyboard.get_keyboard())
            except Exception as s:
                print(s)
                vk.messages.send(user_id=uid, message='Что-то пошло не так,но мы все исправим',
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
            if float(mailing[item["period"]][item["currency"]]) <= item["percent"] >= 0:
                message = f"❗ за {d[item['period']]} курс {item['code']} вырос на {mailing[item['period']][item['currency']]}% ❗"
                vk.messages.send(user_id=item['uid'], random_id=get_random_id(), message=message)
            elif float(mailing[item["period"]][item["currency"]]) >= item["percent"] <= 0:
                message = f"❗ за {d[item['period']]} курс {item['code']} понизился на {abs(float(mailing[item['period']][item['currency']]))}% ❗"
                vk.messages.send(user_id=item['uid'], random_id=get_random_id(), message=message)
        except Exception:
            pass
        time.sleep(1)


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
t = threading.Thread(target=go)
t.start()

if __name__ == '__main__':
    load_new_data()
    main()
