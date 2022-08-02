import click


def w(*msgs):
    cl()
    click.echo("\n".join(msgs), nl=False)


def cl():
    click.clear()
    # click.echo("\x1b[2K\r", nl=False)


def prompt(msg):
    cl()
    val = input(f"{msg}\n")
    click.clear()
    return val
