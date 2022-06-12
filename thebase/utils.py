import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path


DATE_TIME_FORMAT = "%y/%m/%d %H:%M:%S"
BASE_SECRET_PATH = str(Path.home()) + "/.vysacharity/"


class SecretType(Enum):
    tokens = 1
    credentials = 2


class TokenStatus(Enum):
    NEED_NEW_REQUEST = 1
    NEED_REFRESH = 2
    OK = 3


def tokens_status():
    path = BASE_SECRET_PATH + SecretType.tokens.name
    if not os.path.exists(path):
        return TokenStatus.NEED_NEW_REQUEST, None

    with open(path, "r") as f:
        tokens = json.load(f)

    now = datetime.now()
    access_token_expires_at = datetime.strptime(tokens["access_token_expires_at"], DATE_TIME_FORMAT)
    refresh_token_expires_at = datetime.strptime(tokens["refresh_token_expires_at"], DATE_TIME_FORMAT)
    if now < access_token_expires_at:
        return TokenStatus.OK, tokens["access_token"]
    elif now < refresh_token_expires_at:
        return TokenStatus.NEED_REFRESH, tokens["refresh_token"]
    else:
        return TokenStatus.NEED_NEW_REQUEST, None


def get_credentials():
    path = BASE_SECRET_PATH + SecretType.credentials.name
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def write_token(tokens):
    _write_secrets(SecretType.tokens.name, tokens)


def write_creds(creds):
    _write_secrets(SecretType.credentials.name, creds)


def _write_secrets(secret_type, content):
    path = BASE_SECRET_PATH + secret_type
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(content, f, indent=2)
