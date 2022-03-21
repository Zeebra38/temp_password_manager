from flask import Flask, jsonify, abort, make_response, request
from database import db, User, Login, get_logins_by_token, get_logins_by_site, get_login_by_login_id, get_user_by_token
from generators import generate_token, generate_login, generate_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'status': 'error', 'error': 'Not found'}), 404)


@app.route('/')
def hello_page():
    return 'Hello, welcome to temporary passwords manager'


@app.route('/pwd.mng/api/v1.0/logins', methods=['GET'])
def get_logins():
    token = request.args.get('token', default='-1', type=str)
    if token == '-1':
        return make_response(jsonify({'status': 'error', 'error': 'You need to pass token parameter'}), 403)
    res = get_logins_by_token(token)
    if res == -1:
        return make_response(jsonify({'status': 'error', 'error': 'Wrong token'}))
    return jsonify({'status': 'successful', 'Logins:': res}), 200


@app.route('/pwd.mng/api/v1.0/logins', methods=['POST'])
def create_login():
    if not request.json or 'login' not in request.json or 'password' not in request.json:
        return make_response(jsonify({'status': 'error', 'error': 'You must append json'}), 400)
    token = request.args.get('token', default='-1', type=str)
    if token == '-1':
        return make_response(jsonify({'status': 'error', 'error': 'You need to pass token parameter'}), 403)
    user = get_user_by_token(token)
    if user is None:
        return make_response(jsonify({'status': 'error', 'error': 'Wrong token'}), 403)
    new_login = Login(login=request.json['login'], password=request.json['password'], site=request.json.get('site', ''),
                      user=user)
    db.session.add(new_login)
    db.session.commit()
    return jsonify({'status': 'successful'}), 200


@app.route('/pwd.mng/api/v1.0/logins/<int:login_id>', methods=['GET'])
def get_login(login_id):
    token = request.args.get('token', default='-1', type=str)
    if token == '-1':
        return make_response(jsonify({'status': 'error', 'error': 'You need to pass token parameter'}), 403)
    res = get_login_by_login_id(token, login_id)
    if res == -1:
        return make_response(jsonify({'status': 'error', 'error': 'Wrong token'})), 403
    return make_response(jsonify({'status': 'successful', 'login': res})), 200


@app.route('/pwd.mng/api/v1.0/register', methods=['POST'])
def register():
    print(request.json)
    if not request.json or 'username' not in request.json:
        abort(400)
    new_token = generate_token()
    new_user = User(username=request.json['username'], token=new_token)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'status': 'successful', 'token': new_token}), 200


if __name__ == '__main__':
    app.run()
