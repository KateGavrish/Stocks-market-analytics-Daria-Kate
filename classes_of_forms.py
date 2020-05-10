from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, DateField, SelectMultipleField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
import datetime
from scripts.functions import list_of_tuples_id_and_name
from wtforms.widgets import ListWidget, CheckboxInput


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])

    submit = SubmitField('Зарегистрироваться')


class DateForm(FlaskForm):
    date_to = DateField('finish', validators=[DataRequired()], default=datetime.date.today())
    date_from = DateField('start', validators=[DataRequired()], default=datetime.date.today() - datetime.timedelta(days=30))

    submit = SubmitField('Загрузить')


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class EditPreferencesForm(FlaskForm):
    files = list_of_tuples_id_and_name()
    example = MultiCheckboxField('Label', choices=files)

    submit = SubmitField('Сохранить')


class Search(FlaskForm):
    search = StringField('Поиск', validators=[DataRequired()])
    submit = SubmitField('Найти')
