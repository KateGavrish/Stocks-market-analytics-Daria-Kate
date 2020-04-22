import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from datetime import datetime
import schedule

from config import LOGIN, PASSWORD, TOKEN_VK, GROUP_ID
from scripts.functions import *
from scripts.excel_func import create_excel_chart

users_data = {}
flags = {'AU': '🇦🇺', 'AZ': '🇦🇿', 'GB': '🇬🇧', 'AM': '🇦🇲', 'BY': '🇧🇾', 'BG': '🇧🇬', 'BR': '🇧🇷', 'HU': '🇭🇺',
         'HK': '🇭🇰', 'DK': '🇩🇰', 'US': '🇺🇸', 'EU': '🇪🇺', 'IN': '🇮🇳', 'KZ': '🇰🇿', 'CA': '🇨🇦', 'KG': '🇰🇬',
         'CN': '🇨🇳', 'MD': '🇲🇩', 'NO': '🇳🇴', 'PL': '🇵🇱', 'RO': '🇷🇴', 'SG': '🇸🇬', 'TJ': '🇹🇯', 'TR': '🇹🇷',
         'TM': '🇹🇲', 'UZ': '🇺🇿', 'UA': '🇺🇦', 'CZ': '🇨🇿', 'SE': '🇸🇪', 'CH': '🇨🇭', 'ZA': '🇿🇦', 'KR': '🇰🇷',
         'JP': '🇯🇵'}


class MessageError(Exception):
    pass


def load_new_data():
    global data, cur_id
    date = datetime.date.today().strftime('%d/%m/%Y')
    data = daily_data_of_all(date)["ValCurs"]["Valute"]
    cur_id = {i + 1: data[i]["@ID"] for i in range(len(data))}


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
        keyboard.add_button('помощь', color=VkKeyboardColor.PRIMARY)
    else:
        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Вернуться в меню', color=VkKeyboardColor.NEGATIVE)
    return keyboard


def new_user(response, vk, uid):
    message = f"Привет, {response[0]['first_name']}!"
    vk.messages.send(user_id=uid,
                     message=message,
                     random_id=get_random_id())
    menu()


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
    global cur_id, data
    currency = [str(n + 1) + ' ' + flags.get(item["CharCode"][:2], " ") + f'{item["CharCode"]}' for n, item in enumerate(data)]
    vk.messages.send(user_id=uid, message='Выберите валюту\n' + '\n'.join(currency),
                     random_id=get_random_id())
    users_data[uid]['state'] = 3


def check_the_currency_selection(vk, uid, text):
    text = text.rstrip().lstrip()
    try:
        users_data[uid]['currency'] = cur_id[int(text)]
    except Exception:
        raise MessageError
    users_data[uid]['currency'] = 3
    vk.messages.send(user_id=uid, message=f'Введите дату начала и конца периода, за который вы хотите увидеть информацию, в формате YY.mm.dd-YY.mm.dd',
                     random_id=get_random_id())


def show_all(vk, uid):
    global data
    message = [flags.get(item["CharCode"][:2], " ") + f'{item["Nominal"]} {item["CharCode"]}' + f' {item["Value"]} ₽'
               for item in data]
    vk.messages.send(user_id=uid, message='текущий курс\n' + '\n'.join(message),
                     random_id=get_random_id(), keyboard=generate_keyboard(2).get_keyboard())


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
                elif event.message.text.lower() in ['меню', 'вернуться в меню']:
                    menu(vk, uid)
                elif users_data[uid]['state'] == 2:
                    if event.message.text.lower() == 'текущий курс':
                        show_all(vk, uid)
                    elif event.message.text.lower() == 'выбрать валюту':
                        choose_currency(vk, uid)
                    elif event.message.text.lower() == 'помощь':
                        show_help(vk, uid)
                    else:
                        raise MessageError
                elif users_data[uid]['state'] == 3:
                    check_the_currency_selection(vk, uid, event.message.text)
                elif users_data[uid]['state'] == 4:
                    pass
                else:
                    raise MessageError
            except MessageError:
                keyboard = generate_keyboard(users_data[uid])
                vk.messages.send(user_id=uid, message='Я тебя не понимаю. Попробуем еще раз?',
                                 random_id=get_random_id(), keyboard=keyboard.get_keyboard())


# primary — синяя кнопка, обозначает основное действие. #5181B8
# secondary — обычная белая кнопка. #FFFFFF
# negative — опасное действие, или отрицательное действие (отклонить, удалить и тд). #E64646
# positive — согласиться, подтвердить. #4BB34B


if __name__ == '__main__':
    schedule.every().day.at("06:00").do(load_new_data)
    schedule.every().day.at("12:00").do(load_new_data)
    schedule.every().day.at("18:00").do(load_new_data)
    load_new_data()
    main()
