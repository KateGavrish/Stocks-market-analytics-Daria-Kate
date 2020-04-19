import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from config import LOGIN, PASSWORD, TOKEN_VK, GROUP_ID

users_data = {}


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
        keyboard.add_button('помощь', color=VkKeyboardColor.PRIMARY)
    else:
        return None
    return keyboard


def new_user(response, vk, uid):
    message = f"Привет, {response[0]['first_name']}!"
    users_data[uid] = 1
    vk.messages.send(user_id=uid,
                     message=message,
                     random_id=get_random_id())
    menu(vk, uid)


def menu(vk, uid):
    users_data[uid] = 2
    keyboard = generate_keyboard(2)
    vk.messages.send(user_id=uid,
                     message='Добро пожаловать в меню', keyboard=keyboard.get_keyboard(),
                     random_id=get_random_id())


def show_help(vk, uid):
    vk.messages.send(user_id=uid, message='Здесь должна быть помощь',
                     random_id=get_random_id())
    users_data[uid] = 1


def choose_currency(vk, uid):
    vk.messages.send(user_id=uid, message='Здесь должен быть выбор валюты',
                     random_id=get_random_id())
    users_data[uid] = 3


def show_all(vk, uid):
    vk.messages.send(user_id=uid, message='текущий курс',
                     random_id=get_random_id())
    users_data[uid] = 1


def main():
    vk_session = vk_api.VkApi(token=TOKEN_VK)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            uid = event.message.from_id
            response = vk.users.get(user_id=uid)
            users_data[uid] = users_data.get(uid, 0)
            try:
                if users_data[uid] == 0:
                    new_user(response, vk, uid)
                elif users_data[uid] == 1:
                    menu(vk, uid)
                elif users_data[uid] == 2:
                    if event.message.text.lower() == 'текущий курс':
                        show_all(vk, uid)
                    elif event.message.text.lower() == 'выбрать валюту':
                        choose_currency(vk, uid)
                    elif event.message.text.lower() == 'помощь':
                        show_help(vk, uid)
                    else:
                        raise MessageError
                elif users_data[uid] == 3:
                    pass  # выбор валюты
                else:
                    raise MessageError
            except MessageError:
                keyboard = generate_keyboard(users_data[uid])
                vk.messages.send(user_id=uid, message='Я тебя не понимаю. Попробем еще раз?',
                                 random_id=get_random_id(), keyboard=keyboard.get_keyboard())


# primary — синяя кнопка, обозначает основное действие. #5181B8
# secondary — обычная белая кнопка. #FFFFFF
# negative — опасное действие, или отрицательное действие (отклонить, удалить и тд). #E64646
# positive — согласиться, подтвердить. #4BB34B


if __name__ == '__main__':
    main()
