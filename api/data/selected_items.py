import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from .users import User

from .db_session import SqlAlchemyBase


class Items(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'items'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    item = sqlalchemy.Column(sqlalchemy.String) #  вводить id валют через -
    user = orm.relationship('User')
