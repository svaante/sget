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
@click.option('--groups', prompt=True, default='')
def add(content, description, name):
    content = ' '.join(content).strip()
    description = description.strip()
    name = name.strip()
    if groups:
        groups = groups.strip().split(',')
    click.echo(api.add(content, description, name, groups))


@cli.command()
@click.argument('snippet_file', type=click.File('r'), nargs=1)
@click.option('--description', prompt=True)
@click.option('--name', prompt=True)
@click.option('--groups', prompt=True, default='None')
def fadd(snippet_file, description, name, groups):
    description = description.strip()
    name = name.strip()
    if groups:
        groups = groups.strip().split(',')
    click.echo(api.fadd(snippet_file, description, name, groups))


@cli.command()
@click.argument('name', default=None, required=False, nargs=-1)
def rm(name):
    if name:
        name = ' '.join(name)
    try:
        api.rm(name)
        click.echo('Snippet removed!')
    except LookupError as e:
        click.echo(str(e))


@cli.command()
@click.argument('name', default=None, required=False, nargs=-1)
def get(name):
    if name:
        name = ' '.join(name)
    try:
        api.get(name)
        click.echo('Snippet copied to clipboard!')
    except LookupError as e:
        click.echo(str(e))


@cli.command()
@click.argument('name', default=None, required=False)
def share(name):
    if name:
        name = ' '.join(name)
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
