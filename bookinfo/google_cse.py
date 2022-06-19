from urllib.parse import urlencode
import requests


class GoogleCSEImage:
    def __init__(self, cse_id, api_key):
        self._base_url = "https://customsearch.googleapis.com/customsearch/v1?"
        self._cse_id = cse_id
        self._api_key = api_key

    def search_for_links(self, query_str):
        query = {
            "cx": self._cse_id,
            "searchType": "image",
            "key": self._api_key,
            "q": query_str
        }
        resp = requests.get(self._base_url + urlencode(query))
        resp.raise_for_status()

        items = resp.json().get("items")
        return [item["link"] for item in items] if items is not None else None
