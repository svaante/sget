import click

from snip import api


@click.group()
def cli():
    pass


@cli.command()
@click.argument('content', type=str)
@click.option('--description', prompt=True)
def add(content, description):
    api.add(content, description)


@cli.command()
def list():
    api.list()


@cli.command()
def clear():
    api.clear()


@cli.command()
def rm():
    api.rm()


@cli.command()
def run():
    snip = api.run()


if __name__ == '__main__':
    cli()
