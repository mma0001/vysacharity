import time

import click


def w(msg):
    cl()
    click.echo(msg, nl=False)


def cl():
    click.echo("\x1b[2K\r", nl=False)


def prompt(msg):
    cl()
    val = input(f"{msg}\n")
    click.clear()
    return val
