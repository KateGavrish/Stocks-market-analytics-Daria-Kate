from flask import Flask, render_template, redirect, request, send_from_directory
from requests import get, post, put, delete
import pandas as pd
from fbprophet import Prophet
from api.data import db_session
from api.data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_googlecharts import GoogleCharts, LineChart
import yfinance as yf
from api.data.selected_items import Items
from classes_of_forms import *
from datetime import datetime
from scripts.functions import *
from scripts.forex import *
from scripts.excel_func import create

import schedule
import threading
from shutil import rmtree
from os.path import abspath
from os import mkdir, getenv

from scripts.parser import parse_news

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)
charts = GoogleCharts(app)

# HOST = 'https://api-stocks-kate-daria.herokuapp.com/'
with open('static/static_data/tickers.txt', 'r') as f:
    a = f.readlines()[0].split(',')


HOST = getenv("HOST", "")


@login_manager.user_loader
def load_user(user_id):
    a = get(f'{HOST}/api/users/{user_id}').json()
    if 'users' in a:
        user = User()
        user.name = a['users']['name']
        user.surname = a['users']['surname']
        user.hashed_password = a['users']['hashed_password']
        user.email = a['users']['email']
        user.id = a['users']['id']
        return user
    return None


@app.route('/stocks/<ticker>', methods=['GET', 'POST'])
def stocks_one(ticker):
    form = DateForm()
    date_from = form.date_from.data
    date_to = form.date_to.data
    message = " "
    try:
        data = yf.download(ticker, start=date_from, end=date_to).iloc[:, 0:4]
    except Exception:
        message = "Что-то пошло не так. Попробуйте ввести другую дату"
        date_from = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        data = yf.download(ticker, start=date_from).iloc[:, 0:4]

    msft = yf.Ticker(ticker)
    info = msft.info
    try:
        forecast = pd.read_csv(f'static/static_data/{ticker}.csv')
        i = True
    except:
        forecast = []
        i = False

    open = LineChart("open", options={'title': f'{ticker} Open', 'width': '100%'})
    high = LineChart("high", options={'title': f'{ticker} High', 'width': '100%'})
    low = LineChart("low", options={'title': f'{ticker} Low', 'width': '100%'})
    close = LineChart("close", options={'title': f'{ticker} Close', 'width': '100%'})
    if not forecast.empty:
        pred1 = LineChart("pred1", options={'title': f'{ticker} prediction High', 'width': '100%'})
        pred2 = LineChart("pred2", options={'title': f'{ticker} prediction Close', 'width': '100%'})
        pred3 = LineChart("pred3", options={'title': f'{ticker} prediction Low', 'width': '100%'})

    open.add_column("string", "Дата")
    high.add_column("string", "Дата")
    low.add_column("string", "Дата")
    close.add_column("string", "Дата")
    if not forecast.empty:
        pred1.add_column("string", "Дата")
        pred2.add_column("string", "Дата")
        pred3.add_column("string", "Дата")

    open.add_column("number", "Open")
    high.add_column("number", "High")
    low.add_column("number", "Low")
    close.add_column("number", "Close")
    if not forecast.empty:
        pred1.add_column("number", "Prediction high")
        pred2.add_column("number", "Prediction close")
        pred3.add_column("number", "Prediction low")

    open.add_rows(list(zip(*[data.index] + [data['Open'].values.tolist()])))
    high.add_rows(list(zip(*[data.index] + [data['High'].values.tolist()])))
    low.add_rows(list(zip(*[data.index] + [data['Low'].values.tolist()])))
    close.add_rows(list(zip(*[data.index] + [data['Close'].values.tolist()])))
    if not forecast.empty:
        pred1.add_rows(list(zip(*[forecast['ds']] + [forecast['yhat_upper'].values.tolist()])))
        pred2.add_rows(list(zip(*[forecast['ds']] + [forecast['yhat'].values.tolist()])))
        pred3.add_rows(list(zip(*[forecast['ds']] + [forecast['yhat_lower'].values.tolist()])))

    charts.register(open)
    charts.register(high)
    charts.register(low)
    charts.register(close)
    if not forecast.empty:
        charts.register(pred1)
        charts.register(pred2)
        charts.register(pred3)

    return render_template('stocks_one.html', form=form, message=message, ticker=ticker, info=info, i=i)


@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    global a

    def table():
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
        return b

    form = Search()
    date = (datetime.date.today() - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    if request.method == 'POST' and form.validate_on_submit():
        tick = form.search.data.upper()
        try:
            data = yf.download(tick, start=date)
            if not data.empty and tick not in a:
                a.append(tick)
                with open('static/static_data/tickers.txt', 'w') as f:
                    f.write(','.join(a))
            b = table()
            return render_template('stocks.html', params=b, form=form)
        except Exception as e:
            print(e)
    b = table()
    return render_template('stocks.html', params=b, form=form)


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
    data_ = [{'name': code, 'chart_name': name, 'data': data[1:]}]
    create(data_, filename)  # создание excel файла
    return send_from_directory('static/excel', filename, as_attachment=True)


@app.route('/download_csv/<filename>/<ticker>/<date_from>/<date_to>')
def download_csv_stocks(filename, ticker, date_from, date_to):
    try:
        yf.download(ticker, start=date_from, end=date_to).iloc[:, 0:4].to_csv('static/excel/chart_csv.csv')
    except Exception as e:
        print(e)
    return send_from_directory('static/excel', filename, as_attachment=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
            return render_template('login.html', message='', form=form)
    else:
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/edit_password', methods=['GET', 'POST'])
@login_required
def edit_password():
    form = EditPassword()
    if form.validate_on_submit():
        old_pass = form.old_password.data
        new_pass = form.new_password.data
        user = get(f'{HOST}/api/users/login/{current_user.email}/{old_pass}').json()
        if 'error' not in user:
            put(f'{HOST}/api/users/{current_user.id}', json={
                'name': user['users']['name'], 'surname': user['users']['surname'], 'email': user['users']['email'],
                'password': new_pass}).json()
            return render_template('edit_password.html', form=form, message='ваш пароль успешно изменен')
        else:
            return render_template('edit_password.html', form=form, message='неправильный текущий пароль')
    return render_template('edit_password.html', form=form)


@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteForm()
    if form.validate_on_submit():
        user = get(f'{HOST}/api/users/login/{current_user.email}/{form.password.data}').json()
        if 'error' not in user:
            delete(f'{HOST}/api/users/{current_user.id}').json()
            return redirect('/')
        else:
            return render_template('delete_account.html', form=form, message='неправильный пароль')
    return render_template('delete_account.html', form=form)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def user_account():
    date = datetime.date(2020, 3, 28).strftime('%d/%m/%Y')
    list_id_curr = get(f'{HOST}/api/items_of_user/{current_user.id}').json()
    if 'error' not in list_id_curr:
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


@app.route('/news')
def news():
    news = parse_news()
    return render_template('news.html', news=news, date=datetime.datetime.today().strftime('%d.%m.%Y'))


@app.route('/calculate', methods=['GET', 'POST'])
def calc():
    form1 = CalcForm()
    form2 = ConvertForm()
    count1 = ''
    count2 = ''
    n = ''
    new = ''
    new_curr = ''
    if request.method == 'POST' and form1.validate_on_submit():
        try:
            date2 = form1.date1.data.strftime('%Y-%m-%d')
            date1 = form1.date2.data.strftime('%Y-%m-%d')
            base_curr = form1.v1.data
            new_curr = form1.v2.data
            amount1 = float(form1.amount1.data.replace(',', '.'))
            amount2 = float(form1.amount2.data.replace(',', '.'))
            count1 = first_to_second(date1, base_curr, new_curr, amount1)
            count2 = first_to_second(date2, base_curr, new_curr, amount2)
            n = "{0:.3f}".format(count2 / count1)
        except:
            pass

    if request.method == 'POST' and form2.validate_on_submit():
        try:
            base_curr = form2.v1.data
            new_curr = form2.v2.data
            amount = float(form2.amount.data.replace(',', '.'))
            count = first_to_second(datetime.datetime.today().strftime('%Y-%m-%d'), base_curr, new_curr, amount)
            new = "{0:.3f}".format(count)
        except:
            pass

    return render_template('calc.html', form1=form1, form2=form2, count1=count1, n=n,
                           count2=count2, new=new, new_curr=new_curr)


def go():
    while True:
        schedule.run_pending()


def clear_excel():
    try:
        rmtree(abspath('static/excel'))
        mkdir('static/excel')
    except Exception as s:
        pass


schedule.every().hour.at(':10').do(clear_excel)
t = threading.Thread(target=go)
t.start()


def load_data():
    for ticker in a:
        try:
            trend_df = yf.download(ticker, start='2010-01-05')
            predictions = 60
            train_df = trend_df[:-predictions]
            train_df.reset_index(inplace=True)
            train_df.rename(columns={'Date': 'ds', 'Close': 'y', 'High': 'yhat_upper', 'Low': 'yhat_lower'}, inplace=True)
            m = Prophet(changepoint_prior_scale=0.1)
            m.fit(train_df)
            future = m.make_future_dataframe(periods=300)
            m.predict(future)[['ds', 'yhat_upper', 'yhat', 'yhat_lower']].tail(200).to_csv(
                f'static/static_data/{ticker}.csv')
        except:
            pass


schedule.every().day.at('00:00').do(load_data)
t = threading.Thread(target=go)
t.start()
