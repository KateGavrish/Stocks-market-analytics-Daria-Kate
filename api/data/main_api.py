import flask
from flask import Flask, jsonify
from flask_restful import reqparse, Api, Resource

from api.data.users import User
from api.data.db_session import *
from data.selected_items import Items

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('surname')
parser.add_argument('email')
parser.add_argument('password')
parser.add_argument('item')
blueprint = flask.Blueprint('news_api', __name__, template_folder='templates')


def abort_if_users_not_found(user_id):
    session = create_session()
    user = session.query(User).get(user_id)
    if not user:
        jsonify(message=f"User {user_id} not found")


def abort_if_items_not_found(item_id):
    session = create_session()
    user = session.query(User).get(item_id)
    if not user:
        jsonify(message=f"Item {item_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_users_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        return jsonify({'users': user.to_dict(only=('name', 'surname', 'email', 'id'))})

    def delete(self, user_id):
        abort_if_users_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
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
        abort_if_items_not_found(item_id)
        session = create_session()
        item = session.query(Items).get(item_id)
        return jsonify({'item': item.to_dict(only=('item', 'user'))})

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
        return jsonify({'items': [item.to_dict(only=('item', 'user')) for item in items]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        item = Items()
        item.item = args['item'],
        item.user = args['user_id'],
        session.add(item)
        session.commit()
        return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<str:email>',  methods=['GET'])
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


@blueprint.route('/api/users/login/<str:email>/<str:password>',  methods=['POST'])
def user_login(email, password):
    session = create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return jsonify({'error': 'Not found'})
    if user.check_password(password):
        return user


@blueprint.route('/api/users/load/<int:user_id>',  methods=['GET'])
def load_us(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@blueprint.route('/api/items_of_user/<int:user_id>',  methods=['GET'])
def load_items(user_id):
    session = create_session()
    return session.query(Items).filter(Items.user == user_id).first()


def main():
    global_init("/Users/gavrishekaterina/PycharmProjects/YandexLyceum/Stocks-market-analytics-Daria-Kate/api/db/user_data.sqlite")
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource, '/api/users/<int:user_id>')
    api.add_resource(ItemsListResource, '/api/items')
    api.add_resource(ItemsResource, '/api/items/<int:item_id>')
    app.run()


if __name__ == '__main__':
    main()

