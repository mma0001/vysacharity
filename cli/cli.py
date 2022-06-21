import io
import re

from PIL import Image
import click
import requests

from cli.app import App


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
    click.echo("Setting up application...")
    app = App()
    categories = app.the_base_client.categories.get()

    # Input: isbn,book_id
    click.echo("Enter books to add, one line per book, follow this format: ISBN,Book_Id")
    books_raw = click.edit()
    if books_raw is None:
        click.echo("Input is empty, exit.")
        exit(0)

    unprocessed_list = []
    for book_raw in books_raw.splitlines():
        split = [s.strip() for s in book_raw.split(",")]
        isbn = split[0]
        book_id = split[1]
        unprocessed_list.append(book_id)
        book_cat = re.sub(r'\d+', '', book_id)
        book_cat_id = categories[book_cat]
        try:
            _add_one(app, isbn, book_id, book_cat_id)
            unprocessed_list.remove(book_id)
        except Exception as e:
            click.echo(f"Error processing book {book_id}: {e}", err=True)
            click.echo()

    if len(unprocessed_list) > 0:
        click.echo("Here are unprocessed books:", err=True)
        for unprocessed_book in unprocessed_list:
            click.echo(unprocessed_book, err=True)


def _add_one(app, isbn, book_id, cat_id):
    click.echo("==========================================")
    click.echo(f"Finding book [{book_id}] - ISBN:{isbn}...")
    simple_info = app.google_books.search_by_isbn(isbn)

    if simple_info is None:
        raise Exception(f"Book {isbn} not found. Maybe try different ISBN format (ISBN10, ISBN13)?")

    click.echo()
    title = simple_info["title"]
    authors = simple_info["authors"]
    click.echo(f"Title: {title}")
    click.echo(f"Author(s): {', '.join(authors)}")

    click.echo()
    click.echo("Add or modify the description as you see fit, SAVE the text file before close it")
    description = click.edit(simple_info['description'])
    click.echo(f"Description: {description}")

    click.echo()
    img_link = simple_info.get("image")
    if img_link is None:
        click.echo("Finding book covers with Google image search...")
        links = app.cse_image.search_for_links(f"{title} {authors[0]} books")

        if links is None:
            click.echo("No image found! You can: (1) paste an image link or (2) continue without an image")
            while True:
                c = click.getchar()
                if c == '1':
                    img_link = input("Image link: \n")
                    break
                elif c == '2':
                    click.echo("Continuing without book cover")
                    break

        response = requests.get(links[0])
        image_bytes = io.BytesIO(response.content)
        img = Image.open(image_bytes)
        img.show()

        click.echo("Is this cover OK? (y)es/(n)o")
        while True:
            c = click.getchar()
            if c == 'y':
                img_link = links[0]
                break
            elif c == 'n':
                click.echo("You can: (1) paste an image link or (2) continue without an image")
                while True:
                    c = click.getchar()
                    if c == '1':
                        img_link = input("Image link: \n")
                        break
                    elif c == '2':
                        click.echo("Continuing without book cover")
                        break
                break

        click.echo("Creating item...")
        resp = app.the_base_client.items.add({
            "title": f"[{book_id}] {title}",
            "detail": description
        })
        item_id = resp["item"]["item_id"]

        click.echo("Adding category to item...")
        app.the_base_client.item_categories.add(item_id, cat_id)

        if img_link is not None:
            click.echo("Adding image to item...")
            app.the_base_client.items.add_image(item_id, img_link)

        click.echo("終了しました！")
