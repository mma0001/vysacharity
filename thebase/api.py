import http
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler
from threading import Thread
from urllib.parse import urlencode, parse_qs, urlparse

import requests

from thebase.utils import DATE_TIME_FORMAT

_REDIRECT_URI = "http://localhost:8080"


class CallbackOnce(BaseHTTPRequestHandler):
    code = None

    def do_GET(self):
        CallbackOnce.code = parse_qs(urlparse(self.path).query)["code"][0]
        Thread(target=self.server.shutdown).start()


class Client:
    def __init__(self, client_id, client_secret):
        self._base_url = "https://api.thebase.in/1"
        self._client_id = client_id
        self._client_secret = client_secret
        self.items = Items(self._base_url + "/items")
        self.categories = Categories(self._base_url + "/categories")

    def set_token(self, token):
        self.items.set_token(token)
        self.categories.set_token(token)

    def authorize(self):
        query = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": _REDIRECT_URI,
            "scope": "write_items read_items"
        }
        url = self._base_url + "/oauth/authorize?" + urlencode(query)
        webbrowser.open(url, new=2)
        httpd = http.server.HTTPServer(('', 8080), CallbackOnce)
        httpd.serve_forever()
        return CallbackOnce.code

    def access_token(self, code):
        return self._get_token({
            "grant_type": "authorization_code",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": code,
            "redirect_uri": _REDIRECT_URI
        })

    def refresh_token(self, refresh_token):
        return self._get_token({
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": refresh_token,
            "redirect_uri": _REDIRECT_URI
        })

    def _get_token(self, params):
        url = self._base_url + "/oauth/token?" + urlencode(params)
        resp = requests.post(url)
        resp.raise_for_status()
        json_resp = resp.json()
        self.set_token(json_resp["access_token"])

        now = datetime.now()
        access_token_expires_at = now + timedelta(minutes=59)
        refresh_token_expires_at = now + timedelta(days=29)
        return {
            "access_token": json_resp["access_token"],
            "access_token_expires_at": access_token_expires_at.strftime(DATE_TIME_FORMAT),
            "refresh_token": json_resp["refresh_token"],
            "refresh_token_expires_at": refresh_token_expires_at.strftime(DATE_TIME_FORMAT)
        }


class Resources:
    def __init__(self, base_url):
        self._token = None
        self._base_url = base_url

    def set_token(self, token):
        self._token = token


class Items(Resources):
    def __init__(self, base_url):
        super().__init__(base_url)

    def add(self, data):
        body = {
            "title": data["title"],
            "detail": data["detail"],
            "price": 9999,
            "item_tax_type": 1,
            "stock": 1,
            "visible": 1,
        }
        resp = requests.post(
            self._base_url + "/add",
            data=body,
            headers={
                "Authorization": f"bearer {self._token}"
            }
        )
        resp.raise_for_status()
        return resp.json()

    def add_image(self, item_id, img_url):
        body = {
            "item_id": item_id,
            "image_no": 1,
            "image_url": img_url
        }
        resp = requests.post(
            self._base_url + "/add_image",
            data=body,
            headers={
                "Authorization": f"bearer {self._token}"
            }
        )
        resp.raise_for_status()


class Categories(Resources):
    def __init__(self, base_url):
        super().__init__(base_url)

    def get(self):
        resp = requests.get(
            self._base_url,
            headers={
                "Authorization": f"bearer {self._token}"
            }
        )
        resp.raise_for_status()
        return resp.json()
