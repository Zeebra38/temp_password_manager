import base64
import hashlib
import hmac
import secrets


def hash_str_and_base64_encode(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    hash_bytes = hashlib.sha512(pwd_bytes).digest()
    hash_bytes = base64.b64encode(hash_bytes)
    hashed_password = hash_bytes.decode('ascii')
    return hashed_password


def gen_salt() -> str:
    return secrets.token_urlsafe(20)


def hash_and_salt_password(password: str) -> str:
    salt = gen_salt()
    hashed_password = hash_str_and_base64_encode(salt + password)
    return f'{salt}${hashed_password}'


def verify_password(guess: str, true_password: str) -> bool:
    salt, hashed_password = true_password.split('$')
    new_hashed_password = hash_str_and_base64_encode(salt + guess)
    return hmac.compare_digest(hashed_password, new_hashed_password)
