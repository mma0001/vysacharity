import json
import os

from datetime import datetime
from enum import Enum
from pathlib import Path
from bookinfo import google_cse, google_books
from thebase import api
from cli.utils import *

DATE_TIME_FORMAT = "%y/%m/%d %H:%M:%S"
BASE_SECRET_PATH = str(Path.home()) + "/.vysacharity/"


class SecretType(Enum):
    tokens = 1
    credentials = 2


class TokenStatus(Enum):
    NEED_NEW_REQUEST = 1
    NEED_REFRESH = 2
    OK = 3


class App:
    def __init__(self):
        creds = self._read_secrets(SecretType.credentials.name)
        if creds is None:
            creds = self.set_client_creds()
            App._write_secrets(SecretType.credentials.name, creds)
            w("Credentials saved!")

        self.the_base_client = self._init_the_base_client(creds["the_base"])
        self.cse_image = self._init_cse_image(creds["google_cse"])
        self.google_books = google_books.GoogleBooks()

    @staticmethod
    def _tokens_status():
        tokens = App._read_secrets(SecretType.tokens.name)
        if tokens is None:
            return TokenStatus.NEED_NEW_REQUEST, None

        now = datetime.now()
        access_token_expires_at = datetime.strptime(tokens["access_token_expires_at"], DATE_TIME_FORMAT)
        refresh_token_expires_at = datetime.strptime(tokens["refresh_token_expires_at"], DATE_TIME_FORMAT)

        if now < access_token_expires_at:
            return TokenStatus.OK, tokens["access_token"]
        elif now < refresh_token_expires_at:
            return TokenStatus.NEED_REFRESH, tokens["refresh_token"]
        else:
            return TokenStatus.NEED_NEW_REQUEST, None

    @staticmethod
    def _write_secrets(secret_type, content):
        path = BASE_SECRET_PATH + secret_type
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(content, f, indent=2)

    @staticmethod
    def _read_secrets(secret_type):
        path = BASE_SECRET_PATH + secret_type
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return json.load(f)

    @staticmethod
    def set_client_creds():
        the_base_client_id = prompt("TheBase's client id:")
        the_base_client_secret = prompt("TheBase's client secret:")
        google_cse_id = prompt("Google CSE Id:")
        google_cse_api_key = prompt("Google CSE API key:")
        return {
            "the_base": {
                "client_id": the_base_client_id,
                "client_secret": the_base_client_secret
            },
            "google_cse": {
                "id": google_cse_id,
                "api_key": google_cse_api_key
            }
        }

    @staticmethod
    def _init_the_base_client(creds):
        client = api.Client(creds["client_id"], creds["client_secret"])
        tk_status, token = App._tokens_status()
        if tk_status == TokenStatus.NEED_NEW_REQUEST:
            w("Requesting authorization...")
            code = client.authorize()
            w("Getting tokens...")
            tokens = client.access_token(code)
            App._write_secrets(SecretType.tokens.name, tokens)
            w("Tokens saved!")
            token = tokens["access_token"]
        elif tk_status == TokenStatus.NEED_REFRESH:
            w("Refreshing tokens...")
            tokens = client.refresh_token(token)
            App._write_secrets(SecretType.tokens.name, tokens)
            w("Tokens saved!")
            token = tokens["access_token"]
        client.set_token(token)

        return client

    @staticmethod
    def _init_cse_image(creds):
        client = google_cse.GoogleCSEImage(creds["id"], creds["api_key"])
        return client
