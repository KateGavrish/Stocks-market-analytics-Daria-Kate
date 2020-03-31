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
    return render_template('index.html', currency=daily_data_of_all(date)["ValCurs"]["Valute"])


@app.route('/currencies/<code>')
def currencies_page(code):
    cur_id, name = from_code_to_id(code, True)
    data = data_of_one_curr_for_a_per('12/02/2020', '15/02/2020', cur_id)["ValCurs"]["Record"]
    data = [['Дата', code]] + list(map(lambda x: [x["@Date"], float(x["Value"].replace(',', '.'))], data))
    print(data)
    return render_template('currency.html', name=name, cur_data=data)


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