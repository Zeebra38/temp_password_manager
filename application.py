from flask import Flask, jsonify, make_response, request

from database import db, User, Login, get_logins_by_token, get_login_by_login_id, get_user_by_token
from generators import generate_token, generate_login, generate_password


def create_app(testing=False):
    app = Flask(__name__)
    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_db.sqlite3'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    base_url = '/pwd.mng/api/v1.0'

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'status': 'error', 'error': error.description}), 404)

    @app.route('/')
    def hello_page():
        return 'Hello, welcome to "Temporary password manager"'

    @app.route(f'{base_url}/logins', methods=['GET'])
    def get_logins():
        token = request.args.get('token', default='-1', type=str)
        if token == '-1':
            return make_response(jsonify({'status': 'error', 'error': 'You need to pass token parameter'}), 401)
        res = get_logins_by_token(token)
        if res == -1:
            return make_response(jsonify({'status': 'error', 'error': 'Wrong token'}), 401)
        return jsonify({'status': 'success', 'logins': res}), 200

    @app.route(f'{base_url}/logins', methods=['POST'])
    def create_login():
        need_generate = bool(request.args.get('generate', default=0, type=int))
        if not need_generate:
            if not request.json or 'login' not in request.json or 'password' not in request.json:
                return make_response(jsonify({'status': 'error', 'error': 'You must append json'}), 400)
        token = request.args.get('token', default='-1', type=str)
        if token == '-1':
            return make_response(jsonify({'status': 'error', 'error': 'You need to pass token parameter'}), 401)
        user = get_user_by_token(token)
        if user is None:
            return make_response(jsonify({'status': 'error', 'error': 'Wrong token'}), 401)
        if not need_generate:
            new_login = Login(login=request.json['login'], password=request.json['password'],
                              site=request.json.get('site', ''), user=user)
        else:
            args: dict = request.json if request.json is not None else {}
            new_login = Login(login=args.get('login', generate_login()),
                              password=args.get('password', generate_password()),
                              site=args.get('site', ''), user=user)
        db.session.add(new_login)
        db.session.commit()
        return make_response(jsonify({'status': 'success', 'login': new_login.to_dict()}), 200)

    @app.route(f'{base_url}/logins/<int:login_id>', methods=['GET', 'PATCH', 'DELETE'])
    def get_or_update_login(login_id):
        token = request.args.get('token', default='-1', type=str)
        if token == '-1':
            return make_response(jsonify({'status': 'error', 'error': 'You need to pass token parameter'}), 401)
        if request.method == 'GET':
            res = get_login_by_login_id(token, login_id)
            if res == -1:
                return make_response(jsonify({'status': 'error', 'error': 'Wrong token'}), 401)
            return make_response(jsonify({'status': 'success', 'login': res}), 200)
        if request.method == 'PATCH':
            user = get_user_by_token(token)
            if user is None:
                return make_response(jsonify({'status': 'error', 'error': 'Wrong token'}), 401)
            if not request.json or 'login' not in request.json or 'password' not in request.json:
                return make_response(jsonify({'status': 'error', 'error': 'You must append json'}), 400)
            login = Login.query.filter_by(user_id=user.id, id=login_id).first_or_404("Wrong login id")
            login.login = request.json['login']
            login.password = request.json['password']
            login.site = request.json.get('site', login.site)
            db.session.commit()
            return make_response(jsonify({'status': 'success', 'login': login.to_dict()}), 201)
        if request.method == 'DELETE':
            user = get_user_by_token(token)
            if user is None:
                return make_response(jsonify({'status': 'error', 'error': 'Wrong token'}), 401)
            login = Login.query.filter_by(user_id=user.id, id=login_id).first_or_404("Wrong login id")
            db.session.delete(login)
            db.session.commit()
            return make_response(jsonify({'status': 'success'}), 200)

    @app.route(f'{base_url}/register', methods=['POST'])
    def register():
        if not request.json or 'username' not in request.json:
            return make_response(jsonify({'status': 'error', 'error': 'You need to pass "username" in JSON'}), 400)
        new_token = generate_token()
        while new_token in db.session.query(User.token).all():
            new_token = generate_token()
        new_user = User(username=request.json['username'], token=new_token)
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'status': 'success', 'token': new_token}), 201)

    @app.route(f'{base_url}/delete_user', methods=['DELETE'])
    def delete_user():
        token = request.args.get('token', default='-1', type=str)
        if token == '-1':
            return make_response(jsonify({'status': 'error', 'error': 'You need to pass token parameter'}), 401)
        user = get_user_by_token(token)
        if user is None:
            return make_response(jsonify({'status': 'error', 'error': 'Wrong token'}), 401)
        logins = Login.query.filter_by(user_id=user.id).all()
        for login in logins:
            db.session.delete(login)
        db.session.delete(user)
        db.session.commit()
        return make_response(jsonify({'status': 'success'}), 200)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
