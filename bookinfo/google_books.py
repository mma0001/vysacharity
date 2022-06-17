import requests
from urllib.parse import urlencode


class GoogleBooks:
    def __init__(self):
        self._base_url = "https://www.googleapis.com/books/v1/volumes?"

    def search_by_isbn(self, isbn):
        resp = requests.get(self._base_url + urlencode({"q": f"isbn:{isbn}"}))
        resp.raise_for_status()
        info = resp.json()
        if info["totalItems"] == 0:
            return None

        # Self link usually contains more information than just search
        self_link = info["items"][0]["selfLink"]
        resp = requests.get(self_link)
        resp.raise_for_status()

        info = resp.json()
        volume_info = info["volumeInfo"]
        simple_info = {
            "title": volume_info["title"],
            "authors": volume_info["authors"],
            # Description can be missing
            "description": volume_info.get("description")
        }

        # Take extra large or large image if available
        img_links = volume_info.get("imageLinks")
        if img_links is not None:
            if img_links.get("extraLarge") is not None:
                simple_info["image"] = img_links.get("extraLarge")
            elif img_links.get("large") is not None:
                simple_info["image"] = img_links.get("large")

        return simple_info
