import click


from snip import api


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        get()


@cli.command()
@click.argument('content', type=str, nargs=-1)
@click.option('--description', prompt=True)
@click.option('--name', prompt=True)
def add(content, description, name):
    content = ' '.join(content)
    if name == '':
        api.add(content, description)
    else:
        api.add(content, description, name)


@cli.command()
@click.argument('name', default=None, required=False)
def rm(name):
    try:
        api.rm(name)
    except LookupError as e:
        click.echo(str(e))


@cli.command()
@click.argument('name', default=None, required=False)
def cp(name):
    try:
        api.cp(name)
    except LookupError as e:
        click.echo(str(e))


@cli.command()
@click.argument('name', default=None, required=False)
def get(name):
    try:
        api.get(name)
    except LookupError as e:
        click.echo(str(e))


@cli.command()
@click.argument('name', default=None, required=False)
def share(name):
    try:
        res = api.share(name)
        click.echo(res)
    except LookupError as e:
        click.echo(str(e))


@cli.command()
def clear():
    api.clear()


@cli.command()
def list():
    api.list()


if __name__ == '__main__':
    cli()
