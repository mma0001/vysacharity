import click
from cli import utils as app_utils
from thebase import utils as thebase_utils


@click.group()
def cli():
    pass


@cli.command()
def configure():
    app_utils.set_client_creds()


@cli.group()
def items():
    pass


@items.command()
def add():
    client = app_utils.init_client()
    categories = thebase_utils.get_categories()
    resp = client.items.add({
        "title": "Cha voi",
        "detail": "Cha voi la mot quyen sach"
    })
    id = resp["item"]["item_id"]
    client.items.add_image(id, "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1563097301l/49697843._SX0_SY0_.jpg")
    client.item_categories.add(id, categories["KNS"])
    # click.echo(resp)
