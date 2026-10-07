import secrets
from datetime import UTC, datetime, timedelta

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(plain_password: str):
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)


def verification_code_generate():

    verification_code = str(secrets.randbelow(900000) + 100000)
    expires_at = datetime.now(UTC) + timedelta(minutes=10)
    return verification_code, expires_at
