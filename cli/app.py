import click
from cli import utils


@click.group()
def cli():
    pass


@cli.command()
def configure():
    utils.set_client_creds()


@cli.group()
def items():
    pass


@items.command()
def add():
    client = utils.init_client()
    resp = client.items.add({
        "title": "Cha voi",
        "detail": "Cha voi la mot quyen sach"
    })
    click.echo(resp)
