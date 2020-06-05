import flask
from flask import Flask, jsonify
from flask_restful import reqparse, Api, Resource

from api.data.users import User
from api.data.db_session import *
from api.data.selected_items import Items
from api.data.mailing import MailingItems

from os import getenv

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('surname')
parser.add_argument('email')
parser.add_argument('password')

parser.add_argument('item')
parser.add_argument('user_id')

parser.add_argument('currency')
parser.add_argument('period')
parser.add_argument('percent')
parser.add_argument('uid')
parser.add_argument('status')
parser.add_argument('code')

blueprint = flask.Blueprint('main_api', __name__, template_folder='templates')


def abort_if_users_not_found(user_id):
    session = create_session()
    user = session.query(User).get(user_id)
    if not user:
        return 'NO'
    return 'OK'


def abort_if_items_not_found(item_id):
    session = create_session()
    user = session.query(Items).get(item_id)
    if not user:
        return 'NO'
    return 'OK'


def abort_if_mailing_not_found(id_):
    session = create_session()
    item = session.query(MailingItems).get(id_)
    if not item:
        jsonify(message=f"Mailing {id_} not found")


class UsersResource(Resource):
    def get(self, user_id):
        a = abort_if_users_not_found(user_id)
        if a == 'OK':
            session = create_session()
            user = session.query(User).get(user_id)
            return jsonify({'users': user.to_dict(only=('name', 'surname', 'email', 'id', 'hashed_password'))})
        return jsonify({'success': 'NO'})

    def delete(self, user_id):
        a = abort_if_users_not_found(user_id)
        if a == 'OK':
            session = create_session()
            user = session.query(User).get(user_id)
            session.delete(user)
            session.commit()
            return jsonify({'success': 'OK'})

    def put(self, user_id):
        a = abort_if_users_not_found(user_id)
        if a == 'OK':
            args = parser.parse_args()
            session = create_session()
            user = session.query(User).get(user_id)
            user.name = args['name']
            user.surname = args['surname']
            user.email = args['email']
            user.set_password(args['password'])
            session.commit()
            return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('name', 'surname', 'email', 'id')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        user = User()
        user.name = args['name']
        user.surname = args['surname']
        user.email = args['email']
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})


class ItemsResource(Resource):
    def get(self, item_id):
        a = abort_if_items_not_found(item_id)
        if a == 'OK':
            session = create_session()
            item = session.query(Items).get(item_id)
            return jsonify({'item': item.to_dict(only=('item', 'user_id'))})
        return jsonify({'success': 'NO'})

    def delete(self, item_id):
        abort_if_items_not_found(item_id)
        session = create_session()
        item = session.query(Items).get(item_id)
        session.delete(item)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, item_id):
        abort_if_items_not_found(item_id)
        session = create_session()
        args = parser.parse_args()
        item = session.query(Items).get(item_id)
        item.item = args['item']
        session.commit()
        return jsonify({'success': 'OK'})


class ItemsListResource(Resource):
    def get(self):
        session = create_session()
        items = session.query(Items).all()
        return jsonify({'items': [item.to_dict(only=('item', 'user_id')) for item in items]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        item = Items()
        item.item = args['item']
        item.user_id = int(args['user_id'])
        session.add(item)
        session.commit()
        return jsonify({'success': 'OK'})


class MailingListResource(Resource):
    def get(self):
        """получение всех подписок всех пользователей"""
        session = create_session()
        items = session.query(MailingItems).all()
        session.close()
        return jsonify({'items': [item.to_dict(only=('currency', 'period', 'percent', 'uid', 'status', 'code')) for item in items]})

    def post(self):
        """добавление подписки"""
        args = parser.parse_args()
        session = create_session()
        item = MailingItems()
        item.currency = args['currency']
        item.period = int(args['period'])
        item.status = bool(args['status'])
        item.percent = float(args['percent'])
        item.code = args['code']
        item.uid = int(args['uid'])
        session.add(item)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class MailingUserResource(Resource):
    def get(self, user_id):
        """получение всех подписок пользователя"""
        session = create_session()
        items = session.query(MailingItems).filter(MailingItems.uid == user_id).all()
        session.close()
        return jsonify({'items': [item.to_dict(only=('id', 'currency', 'period', 'percent', 'uid', 'status', 'code')) for item in items]})

    def delete(self, user_id):
        """отписывает пользователя от всех рассылок"""
        session = create_session()
        items = session.query(MailingItems).filter(MailingItems.uid == user_id).all()
        if items:
            for item in items:
                session.delete(item)
            session.commit()
            session.close()
            return jsonify({'success': 'OK'})
        else:
            session.close()
            return jsonify({'success': 'no subscriptions'})


class MailingResource(Resource):
    def delete(self, id_):
        """удаляет подписку"""
        abort_if_mailing_not_found(id_)
        session = create_session()
        item = session.query(MailingItems).get(id_)
        session.delete(item)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<email>',  methods=['GET'])
def get_user_email(email):
    session = create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return None
    return jsonify(
        {
            'users': user.to_dict(only=('name', 'surname', 'email', 'id'))
        }
    )


@blueprint.route('/api/users/login/<email>/<password>',  methods=['GET'])
def user_login(email, password):
    session = create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return jsonify({'error': 'Not found'})
    if user.check_password(password):
        return jsonify({'users': user.to_dict(only=('name', 'surname', 'email', 'id', 'hashed_password'))})
    else:
        return jsonify({'error': 'Wrong password'})


@blueprint.route('/api/users/load/<int:user_id>',  methods=['GET'])
def load_us(user_id):
    session = create_session()
    user = session.query(User).get(user_id)
    return jsonify(
        {
            'users': user.to_dict(only=('name', 'surname', 'email', 'id', 'hashed_password'))
        }
    )


@blueprint.route('/api/items_of_user/<int:user_id>',  methods=['GET'])
def load_items(user_id):
    session = create_session()
    try:
        item = session.query(Items).filter(Items.user_id == user_id).all()[-1]
        return jsonify({'item': item.to_dict(only=('item', 'user_id'))})
    except Exception:
        return jsonify({'error': 'Not found'})


def main():
    global_init("../db/user_data.sqlite")
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource, '/api/users/<int:user_id>')
    api.add_resource(ItemsListResource, '/api/items')
    api.add_resource(ItemsResource, '/api/items/<int:item_id>')
    api.add_resource(MailingListResource, '/api/mailing')
    api.add_resource(MailingResource, '/api/mailing/<int:id_>')
    api.add_resource(MailingUserResource, '/api/user-mailing-lists/<int:user_id>')
    app.register_blueprint(blueprint)
    app.run()


if __name__ == '__main__':
    main()

