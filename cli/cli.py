import click
from cli.app import App


@click.group()
def cli():
    pass


@cli.group()
def books():
    pass


@books.command()
def add():
    app = App()
    categories = app.the_base_client.categories.get()

