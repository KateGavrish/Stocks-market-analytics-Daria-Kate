from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, DateField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
import datetime


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

    submit = SubmitField('Войти')


class DateForm(FlaskForm):
    date_to = DateField('finish', validators=[DataRequired()], default=datetime.date.today())
    date_from = DateField('start', validators=[DataRequired()], default=datetime.date.today() - datetime.timedelta(days=30))

    submit = SubmitField('Загрузить')


# class EditPreferencesForm(FlaskForm):
#     email = StringField('Почта', validators=[DataRequired()])
#     password = PasswordField('Пароль', validators=[DataRequired()])
#     password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
#     name = StringField('Имя пользователя', validators=[DataRequired()])
#     surname = StringField('Фамилия пользователя', validators=[DataRequired()])
#
#     submit = SubmitField('Войти')