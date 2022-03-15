import string
import re
import random


def generate_login():
    alphabet = string.ascii_letters + string.digits
    while True:
        login = ''.join(random.choices(alphabet, k=random.randint(6, 11)))
        if re.match(r'^[a-zA-Z]\w{5,10}$', login):
            return login


def generate_password():
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(random.choices(alphabet, k=random.randint(10, 14)))
        if re.match(r'^[\w|\W]{10,}$', password):
            return password
