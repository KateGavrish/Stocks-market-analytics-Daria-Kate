from flask import Flask, render_template, redirect, request, send_from_directory
from requests import get, post
# import pandas as pd
from data import db_session
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_googlecharts import GoogleCharts, LineChart
# import yfinance as yf
from data.selected_items import Items
from classes_of_forms import *
from datetime import datetime
from scripts.functions import *
from scripts.excel_func import create_excel_chart

import schedule
import threading
from shutil import rmtree
from os.path import abspath
from os import mkdir

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


login_manager = LoginManager()
login_manager.init_app(app)
charts = GoogleCharts(app)

HOST = 'http://127.0.0.1:5000'


@login_manager.user_loader
def load_user(user_id):
    a = get(f'{HOST}/api/users/{user_id}').json()
    user = User()
    user.name = a['users']['name']
    user.surname = a['users']['surname']
    user.hashed_password = a['users']['hashed_password']
    user.email = a['users']['email']
    user.id = a['users']['id']
    return user


# @app.route('/stocks/<ticker>', methods=['GET', 'POST'])
# def stocks_one(ticker):
#     form = DateForm()
#     date_from = form.date_from.data
#     date_to = form.date_to.data
#     message = " "
#     try:
#         data = data_of_one_curr_for_a_per(date_from.strftime('%d/%m/%Y'),
#                                           date_to.strftime('%d/%m/%Y'), cur_id)["ValCurs"]["Record"]
#         data = [['Дата', code]] + list(map(lambda x: [x["@Date"], float(x["Value"].replace(',', '.'))], data))
#     except Exception:
#         message = "Что-то пошло не так. Попробуйте ввести другую дату"
#         date_to = datetime.date.today()
#         date_from = datetime.date.today() - datetime.timedelta(days=30)
#         data = data_of_one_curr_for_a_per(date_from.strftime('%d/%m/%Y'),
#                                           date_to.strftime('%d/%m/%Y'), cur_id)["ValCurs"]["Record"]
#         data = [['Дата', code]] + list(map(lambda x: [x["@Date"], float(x["Value"].replace(',', '.'))], data))
#
#     create_excel_chart(name, code, data[1:])  # создание excel-файла
#     my_chart = LineChart("my_chart", options={'title': name, 'width': '100%'})
#     my_chart.add_column("string", "Дата")
#     my_chart.add_column("number", "Open")
#     my_chart.add_column("string", "High")
#     my_chart.add_column("number", "Low")
#     my_chart.add_column("string", "Close")
#     my_chart.add_rows(data[1:])
#     charts.register(my_chart)
#
#     return render_template('stocks_one.html', form=form, message=message)


@app.route('/stocks')
def stocks():
    date = datetime.date.today().strftime('%Y-%m-%d')
    a = ['AAPL', 'AAL', 'SPY', 'WWE', 'DAKT', 'ORA', 'CAMP', 'BREW']
    b = []
    for x in a:
        try:
            data = yf.download(x, start=date)
            if not data.empty:
                open = int(data['Open'][0] * 100) / 100
                high = int(data['High'][0] * 100) / 100
                low = int(data['Low'][0] * 100) / 100
                close = int(data['Close'][0] * 100) / 100
                b.append([x, open, high, low, close])
        except Exception:
            pass
    return render_template('stocks.html', params=b)


@app.route('/index')
@app.route('/')
def main_page():
    date = datetime.date.today().strftime('%d/%m/%Y')
    return render_template('index.html', currency=daily_data_of_all(date)["ValCurs"]["Valute"])


@app.route('/currencies/<code>', methods=['GET', 'POST'])
def currencies_page(code):
    form = DateForm()
    date_from = form.date_from.data
    date_to = form.date_to.data
    message = " "
    cur_id, name = from_code_to_id(code, True)
    try:
        data = data_of_one_curr_for_a_per(date_from.strftime('%d/%m/%Y'),
                                          date_to.strftime('%d/%m/%Y'), cur_id)["ValCurs"]["Record"]
        data = [['Дата', code]] + list(map(lambda x: [x["@Date"], float(x["Value"].replace(',', '.'))], data))
    except Exception:
        message = "Что-то пошло не так. Попробуйте ввести другую дату"
        date_to = datetime.date.today()
        date_from = datetime.date.today() - datetime.timedelta(days=30)
        data = data_of_one_curr_for_a_per(date_from.strftime('%d/%m/%Y'),
                                          date_to.strftime('%d/%m/%Y'), cur_id)["ValCurs"]["Record"]
        data = [['Дата', code]] + list(map(lambda x: [x["@Date"], float(x["Value"].replace(',', '.'))], data))
    filename = f'{code}_{date_from}_{date_to}'
    my_chart = LineChart("my_chart", options={'title': name, 'width': '100%'})
    my_chart.add_column("string", "Дата")
    my_chart.add_column("number", "Цена")
    my_chart.add_rows(data[1:])
    charts.register(my_chart)

    return render_template('currency.html', form=form, message=message, name=f"{filename}.xlsx")


@app.route('/download/<filename>')
def download_file(filename):
    code, date_from, date_to = filename.split('.')[0].split('_')
    date_to = '/'.join(date_to.split('-')[::-1])
    date_from = '/'.join(date_from.split('-')[::-1])
    cur_id, name = from_code_to_id(code, True)
    data = data_of_one_curr_for_a_per(date_from, date_to, cur_id)["ValCurs"]["Record"]
    data = [['Дата', code]] + list(map(lambda x: [x["@Date"], float(x["Value"].replace(',', '.'))], data))
    create_excel_chart(name, code, data[1:], filename)  # создание excel файла
    return send_from_directory('static/excel', filename, as_attachment=True)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        if get(f'{HOST}/api/users/{form.email.data}'):
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        post(f'{HOST}/api/users',
             json={'name': form.name.data,
                   'surname': form.surname.data,
                   'email': form.email.data,
                   'password': form.password.data}).json()

        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            a = get(f'{HOST}/api/users/login/{form.email.data}/{form.password.data}').json()
            user = User()
            user.name = a['users']['name']
            user.surname = a['users']['surname']
            user.hashed_password = a['users']['hashed_password']
            user.email = a['users']['email']
            user.id = a['users']['id']
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        except Exception as e:
            return render_template('login.html', message=e, form=form)
    else:
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/account', methods=['GET', 'POST'])
def user_account():
    date = datetime.date(2020, 3, 28).strftime('%d/%m/%Y')
    list_id_curr = get(f'{HOST}/api/items_of_user/{current_user.id}').json()
    if list_id_curr:
        list_id_curr = list_id_curr['item']['item'].split('-')
        params = [x for x in daily_data_of_all(date)["ValCurs"]["Valute"] if x['@ID'] in list_id_curr]
        delta = daily_data_of_all_change(list_id_curr)
    else:
        list_id_curr = [x[0] for x in list_of_tuples_id_and_name()]
        params = daily_data_of_all(date)["ValCurs"]["Valute"]
        delta = daily_data_of_all_change(list_id_curr)
    return render_template('account.html', params=params, delta=delta)


@app.route('/edit_preferences', methods=['GET', 'POST'])
def edit_preferences():
    form = EditPreferencesForm()
    if form.validate_on_submit():
        li = '-'.join(form.example.data)
        post(f'{HOST}/api/items',
             json={
                 'item': li,
                 'user_id': current_user.id
             })

        return redirect('/account')

    return render_template('edit_preferences.html', form=form)


def go():
    while True:
        schedule.run_pending()


def clear_excel():
    try:
        rmtree(abspath('static/excel'))
        mkdir('static/excel')
    except Exception as s:
        pass


schedule.every().hour.at(':00').do(clear_excel)
t = threading.Thread(target=go)
t.start()


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')
