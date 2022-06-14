import json

import click

from thebase import utils, api


def set_client_creds():
    client_id = input("Client id: \n")
    client_secret = input("Client secret: \n")
    utils.write_creds({
        "client_id": client_id,
        "client_secret": client_secret
    })
    click.echo("Credentials saved!")


def init_client():
    creds = utils.get_credentials()
    if creds is None:
        set_client_creds()
        creds = utils.get_credentials()

    client = api.Client(creds["client_id"], creds["client_secret"])
    tokens_status, token = utils.tokens_status()
    if tokens_status == utils.TokenStatus.NEED_NEW_REQUEST:
        click.echo("Requesting authorization...")
        code = client.authorize()
        click.echo("Getting tokens...")
        tokens = client.access_token(code)
        utils.write_token(tokens)
        click.echo("Tokens saved!")
        token = tokens["access_token"]
    elif tokens_status == utils.TokenStatus.NEED_REFRESH:
        click.echo("Refreshing tokens...")
        tokens = client.refresh_token(token)
        utils.write_token(tokens)
        click.echo("Tokens saved!")
        token = tokens["access_token"]
    client.set_token(token)

    if utils.get_categories() is None:
        click.echo("Getting categories...")
        categories = client.categories.get()
        categories_map = {}
        for category in categories["categories"]:
            categories_map[_get_category_abbrev(category["name"])] = category["category_id"]
        utils.write_categories(categories_map)
        click.echo("Categories saved!")
        click.echo(json.dumps(categories_map, indent=2))

    return client


def _get_category_abbrev(category):
    words = category.split()
    abbrev = ""
    for w in words[1:]:
        abbrev += w[0].upper()
        for c in w[1:]:
            abbrev += c if ord('A') <= ord(c) <= ord('Z') else ""
    return abbrev
