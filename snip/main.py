import click

from snip import api


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        run()


@cli.command()
@click.argument('content', type=str, nargs=-1)
@click.option('--description', prompt=True)
def add(content, description):
    api.add(' '.join(content), description)


@cli.command()
def rm():
    api.rm()


@cli.command()
def list():
    api.list()


@cli.command()
def cp():
    api.cp()


@cli.command()
def clear():
    api.clear()


@cli.command()
def run():
    api.run()


if __name__ == '__main__':
    cli()
