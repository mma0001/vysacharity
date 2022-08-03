import io
import re
from cli.utils import *
from PIL import Image
import click
import requests

from cli.app import App


fq_title = None


@click.group()
def cli():
    pass


@cli.group()
def books():
    pass


@books.command()
def add():
    click.clear()

    # Setup resource providers
    w("Setting up application...")
    app = App()
    categories = app.the_base_client.categories.get()

    # Input: isbn,book_id
    w("Enter books to add, one line per book, follow this format: ISBN,Book_Id")
    books_raw = click.edit()
    if books_raw is None:
        w("Input is empty, exit.")
        exit(0)

    unprocessed_list = []
    successful_list = []
    for book_raw in books_raw.splitlines():
        split = [s.strip() for s in book_raw.split(",")]
        isbn = split[0]
        book_id = split[1]
        unprocessed_list.append(book_id)
        book_cat = re.sub(r'\d+', '', book_id)
        book_cat_id = categories[book_cat]
        try:
            isbn, book_id, title, description, authors, has_img = _add_one(app, isbn, book_id, book_cat_id)
            unprocessed_list.remove(book_id)
            successful_list.append(f"{isbn},{book_id},{title},{description},{authors},{has_img}")
        except Exception as e:
            w(f"Error processing book {book_id}: {e}")

    if len(unprocessed_list) > 0:
        click.echo("Here are unprocessed books:", err=True)
        for unprocessed_book in unprocessed_list:
            click.echo(unprocessed_book, err=True)

    click.edit("\n".join(successful_list))


def _add_one(app, isbn, book_id, cat_id):
    w(f"Finding book [{book_id}] - ISBN:{isbn}...")
    simple_info = app.google_books.search_by_isbn(isbn)

    if simple_info is None:
        w(f"Book {isbn} not found. Do you want to submit manually? (y)es/(n)o")
        while True:
            c = click.getchar()
            if c == 'y':
                t = prompt("Enter book title:")
                a = prompt("Enter book authors (if many, separated by commas (,):")
                simple_info = {
                    "title": t,
                    "authors": a
                }
                simple_info["authors"] = simple_info["authors"].split(",")
                break
            elif c == 'n':
                raise Exception(f"Book {isbn} will be put into unprocessed list.")

    title = simple_info["title"]
    authors = simple_info["authors"]

    global fq_title
    fq_title = f"[{book_id}] {title}"

    w(fq_title, "Add or modify the description as you see fit, SAVE the text file before close it")
    description = click.edit(simple_info.get("description"))

    img_link = simple_info.get("image")
    if img_link is None:
        img_link = _search_for_book_cover(app, title, authors)

    w(fq_title, "Creating item...")
    resp = app.the_base_client.items.add({
        "title": f"[{book_id}] {title}",
        "detail": description
    })
    item_id = resp["item"]["item_id"]

    w(fq_title, "Adding category to item...")
    app.the_base_client.item_categories.add(item_id, cat_id)

    if img_link is not None:
        w("Adding image to item...")
        app.the_base_client.items.add_image(item_id, img_link)

    w(fq_title, "終了しました！")
    return isbn, book_id, title, description.replace("\n", " "), " & ".join(authors), "x" if img_link else ""


def _search_for_book_cover(app, title, authors):
    w(fq_title, "Finding book covers with Google image search...")
    links = app.cse_image.search_for_links(f"{title} {authors[0]} books")
    if links is None:
        return _manual_image_link("No image found! ")

    img_link = links[0]
    _show_img(img_link)

    w(fq_title, "Is this cover OK? (y)es/(n)o")
    while True:
        c = click.getchar()
        if c == 'y':
            return img_link
        elif c == 'n':
            return _manual_image_link()


def _manual_image_link(pre_msg=""):
    w(fq_title, f"{pre_msg}You can: (1) paste an image link or (2) continue without an image")
    while True:
        c = click.getchar()
        if c == '1':
            return prompt("Image link:")
        elif c == '2':
            w(fq_title, "Continuing without book cover")
            return


def _show_img(img_link):
    response = requests.get(img_link)
    image_bytes = io.BytesIO(response.content)
    img = Image.open(image_bytes)
    img.show()
