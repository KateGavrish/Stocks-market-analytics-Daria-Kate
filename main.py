from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, IntegerField, FieldList, FormField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data.selected_items import Items

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')