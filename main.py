from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, IntegerField, FieldList, FormField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data.selected_items import Items
from classes_of_forms import *
from datetime import datetime
from scripts.functions import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/index')
@app.route('/')
def main_page():
    date = str(datetime.now().date().strftime('%d/%m/%Y'))
    # val = [{'@ID': 'R01010', 'NumCode': '036', 'CharCode': 'AUD', 'Nominal': '1', 'Name': 'Австралийский доллар', 'Value': '47,1448'}, {'@ID': 'R01020A', 'NumCode': '944', 'CharCode': 'AZN', 'Nominal': '1', 'Name': 'Азербайджанский манат', 'Value': '45,9330'}, {'@ID': 'R01035', 'NumCode': '826', 'CharCode': 'GBP', 'Nominal': '1', 'Name': 'Фунт стерлингов Соединенного королевства', 'Value': '94,5771'}, {'@ID': 'R01060', 'NumCode': '051', 'CharCode': 'AMD', 'Nominal': '100', 'Name': 'Армянских драмов', 'Value': '15,7194'}, {'@ID': 'R01090B', 'NumCode': '933', 'CharCode': 'BYN', 'Nominal': '1', 'Name': 'Белорусский рубль', 'Value': '30,1979'}, {'@ID': 'R01100', 'NumCode': '975', 'CharCode': 'BGN', 'Nominal': '1', 'Name': 'Болгарский лев', 'Value': '43,7979'}, {'@ID': 'R01115', 'NumCode': '986', 'CharCode': 'BRL', 'Nominal': '1', 'Name': 'Бразильский реал', 'Value': '15,4738'}, {'@ID': 'R01135', 'NumCode': '348', 'CharCode': 'HUF', 'Nominal': '100', 'Name': 'Венгерских форинтов', 'Value': '24,2120'}, {'@ID': 'R01200', 'NumCode': '344', 'CharCode': 'HKD', 'Nominal': '1', 'Name': 'Гонконгский доллар', 'Value': '10,0279'}, {'@ID': 'R01215', 'NumCode': '208', 'CharCode': 'DKK', 'Nominal': '1', 'Name': 'Датская крона', 'Value': '11,4760'}, {'@ID': 'R01235', 'NumCode': '840', 'CharCode': 'USD', 'Nominal': '1', 'Name': 'Доллар США', 'Value': '77,7325'}, {'@ID': 'R01239', 'NumCode': '978', 'CharCode': 'EUR', 'Nominal': '1', 'Name': 'Евро', 'Value': '85,7389'}, {'@ID': 'R01270', 'NumCode': '356', 'CharCode': 'INR', 'Nominal': '10', 'Name': 'Индийских рупий', 'Value': '10,3457'}, {'@ID': 'R01335', 'NumCode': '398', 'CharCode': 'KZT', 'Nominal': '100', 'Name': 'Казахстанских тенге', 'Value': '17,4278'}, {'@ID': 'R01350', 'NumCode': '124', 'CharCode': 'CAD', 'Nominal': '1', 'Name': 'Канадский доллар', 'Value': '55,2941'}, {'@ID': 'R01370', 'NumCode': '417', 'CharCode': 'KGS', 'Nominal': '100', 'Name': 'Киргизских сомов', 'Value': '97,2264'}, {'@ID': 'R01375', 'NumCode': '156', 'CharCode': 'CNY', 'Nominal': '1', 'Name': 'Китайский юань', 'Value': '10,9611'}, {'@ID': 'R01500', 'NumCode': '498', 'CharCode': 'MDL', 'Nominal': '10', 'Name': 'Молдавских леев', 'Value': '43,0055'}, {'@ID': 'R01535', 'NumCode': '578', 'CharCode': 'NOK', 'Nominal': '10', 'Name': 'Норвежских крон', 'Value': '73,7766'}, {'@ID': 'R01565', 'NumCode': '985', 'CharCode': 'PLN', 'Nominal': '1', 'Name': 'Польский злотый', 'Value': '18,9301'}, {'@ID': 'R01585F', 'NumCode': '946', 'CharCode': 'RON', 'Nominal': '1', 'Name': 'Румынский лей', 'Value': '17,7184'}, {'@ID': 'R01589', 'NumCode': '960', 'CharCode': 'XDR', 'Nominal': '1', 'Name': 'СДР (специальные права заимствования)', 'Value': '105,7869'}, {'@ID': 'R01625', 'NumCode': '702', 'CharCode': 'SGD', 'Nominal': '1', 'Name': 'Сингапурский доллар', 'Value': '54,2673'}, {'@ID': 'R01670', 'NumCode': '972', 'CharCode': 'TJS', 'Nominal': '10', 'Name': 'Таджикских сомони', 'Value': '76,2457'}, {'@ID': 'R01700J', 'NumCode': '949', 'CharCode': 'TRY', 'Nominal': '1', 'Name': 'Турецкая лира', 'Value': '12,0661'}, {'@ID': 'R01710A', 'NumCode': '934', 'CharCode': 'TMT', 'Nominal': '1', 'Name': 'Новый туркменский манат', 'Value': '22,2411'}, {'@ID': 'R01717', 'NumCode': '860', 'CharCode': 'UZS', 'Nominal': '10000', 'Name': 'Узбекских сумов', 'Value': '81,5430'}, {'@ID': 'R01720', 'NumCode': '980', 'CharCode': 'UAH', 'Nominal': '10', 'Name': 'Украинских гривен', 'Value': '27,5213'}, {'@ID': 'R01760', 'NumCode': '203', 'CharCode': 'CZK', 'Nominal': '10', 'Name': 'Чешских крон', 'Value': '31,5383'}, {'@ID': 'R01770', 'NumCode': '752', 'CharCode': 'SEK', 'Nominal': '10', 'Name': 'Шведских крон', 'Value': '78,0000'}, {'@ID': 'R01775', 'NumCode': '756', 'CharCode': 'CHF', 'Nominal': '1', 'Name': 'Швейцарский франк', 'Value': '80,7191'}, {'@ID': 'R01810', 'NumCode': '710', 'CharCode': 'ZAR', 'Nominal': '10', 'Name': 'Южноафриканских рэндов', 'Value': '44,4059'}, {'@ID': 'R01815', 'NumCode': '410', 'CharCode': 'KRW', 'Nominal': '1000', 'Name': 'Вон Республики Корея', 'Value': '63,7831'}, {'@ID': 'R01820', 'NumCode': '392', 'CharCode': 'JPY', 'Nominal': '100', 'Name': 'Японских иен', 'Value': '71,4027'}]
    return render_template('index.html', currency=daily_data_of_all(date)["ValCurs"]["Valute"])
    # return render_template('index.html', currency=val)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    db_session.global_init("db/user_data.sqlite")
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.set_password(form.password.data)
        session.add(user)
        session.commit()

        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/account")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    else:
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/account', methods=['GET', 'POST'])
def user_account():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')