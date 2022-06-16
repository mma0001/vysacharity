import io

import requests
from PIL import Image

if __name__ == '__main__':
    resp = requests.get("https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1563097301l/49697843._SX0_SY0_.jpg")
    img = Image.open(io.BytesIO(resp.content))
    img.show()
