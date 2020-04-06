from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_googlecharts import GoogleCharts, LineChart
from data.selected_items import Items
from classes_of_forms import *
from datetime import datetime
from scripts.functions import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/user_data.sqlite")
charts = GoogleCharts(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


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
    message = ""
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

    my_chart = LineChart("my_chart", options={'title': name, 'width': '100%'})
    my_chart.add_column("string", "Дата")
    my_chart.add_column("number", "Цена")
    my_chart.add_rows(data[1:])
    charts.register(my_chart)

    return render_template('currency.html', form=form, message=message)


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
            return redirect("/")
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
    session = db_session.create_session()
    items = session.query(Items).filter(Items.user == current_user.id).all()[-1].item.split('-')
    date = datetime.date.today().strftime('%d/%m/%Y')
    params = [item for item in daily_data_of_all(date)["ValCurs"]["Valute"] if item['@ID'] in items]
    list_id_curr = items
    delta = daily_data_of_all_change(list_id_curr)
    return render_template('account.html', params=params, delta=delta)


@app.route('/edit_preferences', methods=['GET', 'POST'])
def edit_preferences():
    form = EditPreferencesForm()
    if form.validate_on_submit():
        li = '-'.join(form.example.data)
        session = db_session.create_session()

        item = Items()
        item.user = current_user.id
        item.item = li

        session.add(item)
        session.commit()
        return redirect('/account')

    return render_template('edit_preferences.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')