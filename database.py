from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from secret_data import secret_key  # секретный ключ str

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(StringEncryptedType(db.String(30), secret_key, AesEngine, 'pkcs5'), nullable=False)
    token = db.Column(StringEncryptedType(db.String(30), secret_key, AesEngine, 'pkcs5'), unique=True, nullable=False)
    user = db.relationship('Login', backref=db.backref('user'))

    def __str__(self):
        return f'<User {self.id} {self.username}>'

    def __repr__(self):
        return f'<User {self.id} {self.username}>'


class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login = db.Column(StringEncryptedType(db.String(30), secret_key, AesEngine, 'pkcs5'), nullable=False)
    password = db.Column(StringEncryptedType(db.String(30), secret_key, AesEngine, 'pkcs5'), nullable=False)
    site = db.Column(StringEncryptedType(db.String(40), secret_key, AesEngine, 'pkcs5'), nullable=True)

    def to_dict(self):
        return {'id': self.id, 'login': self.login, 'password': self.password, 'site': self.site}

    def __str__(self):
        return f'<Data: id={self.id} user_id={self.user_id} login={self.login} password={self.password}>'

    def __repr__(self):
        return f'<Data: id={self.id} user_id={self.user_id} login={self.login} password={self.password}>'


def get_user_by_token(token: str):
    user = User.query.filter_by(token=token).first()
    if user is None:
        return None
    return user


def get_logins_by_token(token: str):
    user = get_user_by_token(token)
    if user is None:
        return -1
    logins = Login.query.filter_by(user_id=user.id).all()
    res = []
    for login in logins:
        res.append({'id': login.id, 'login': login.login, 'password': login.password, 'site': login.site})
    return res


def get_login_by_login_id(token: str, login_id: int):
    user = get_user_by_token(token)
    if user is None:
        return -1
    login = Login.query.filter_by(user_id=user.id, id=login_id).first()
    if login is None:
        return {'id': login_id, 'login': '', 'password': '', 'site': ''}
    return {'id': login_id, 'login': login.login, 'password': login.password, 'site': login.site}
