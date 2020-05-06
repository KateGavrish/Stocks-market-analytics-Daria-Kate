import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class MailingItems(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'mailing'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    currency = sqlalchemy.Column(sqlalchemy.String)
    period = sqlalchemy.Column(sqlalchemy.Integer)
    percent = sqlalchemy.Column(sqlalchemy.Float)
    uid = sqlalchemy.Column(sqlalchemy.Integer)
    status = sqlalchemy.Column(sqlalchemy.Boolean)
    code = sqlalchemy.Column(sqlalchemy.String)