from flask import Flask, jsonify, abort, make_response, request

app = Flask(__name__)

logins = [
    {
        'id': 1,
        'login': u'login1',
        'password': u'qwerty1',
        'site': u'www.google.com'
    },
    {
        'id': 2,
        'login': u'login2',
        'password': u'qwerty2',
        'site': u'www.google.com'
    }
]


def check_login_id(login_id):
    login = list(filter(lambda log: log['id'] == login_id, logins))
    if len(login) == 0:
        return False
    return login[0]


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def hello_page():
    return 'Hello, welcome to temp passwords manager'


@app.route('/pwd.mng/api/v1.0/logins', methods=['GET'])
def get_logins():
    return jsonify({'logins': logins})


@app.route('/pwd.mng/api/v1.0/logins/<int:login_id>', methods=['GET'])
def get_login(login_id):
    res = check_login_id(login_id)
    if res:
        return jsonify({'login': res})
    return abort(404)


@app.route('/pwd.mng/api/v1.0/logins', methods=['POST'])
def create_login():
    if not request.json or not 'login' in request.json or not 'password' in request.json:
        abort(400)
    login = {
        'id': logins[-1]['id'] + 1,
        'login': request.json['login'],
        'password': request.json['password'],
        'site': request.json.get('site', '')
    }
    logins.append(login)
    return jsonify({'login': login}), 201


if __name__ == '__main__':
    app.run(debug=True)
