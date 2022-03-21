import string
import re
import secrets


def generate_login() -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        login = ''.join(secrets.choice(alphabet) for i in range(10))
        if re.match(r'^[a-zA-Z]\w+$', login):
            return login


def generate_password() -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(10))
    return password


def generate_token() -> str:
    return secrets.token_urlsafe(16)
