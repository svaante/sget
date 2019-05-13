import click


from sget import api


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        get()


@cli.command()
@click.argument('content', type=str, nargs=-1)
@click.option('-d', '--description', prompt=True)
@click.option('-n', '--name', prompt=True)
@click.option('-g', '--groups', prompt=True, default='')
def add(content, description, name, groups):
    content = ' '.join(content).strip()
    description = description.strip()
    name = name.strip()
    if groups:
        groups = groups.strip().split(',')
    click.echo(api.add(content, description, name, groups))


@cli.command()
@click.argument('snippet_file', type=click.File('r'), nargs=1)
@click.option('-d', '--description', prompt=True)
@click.option('-n', '--name', prompt=True)
@click.option('-g', '--groups', prompt=True, default='')
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
        msg = 'Snippet successfully removed!'
        _success(msg)
    except Exception as e:
        _error(str(e))


@cli.command()
@click.argument('name', default=None, required=False, nargs=-1)
def get(name):
    if name:
        name = ' '.join(name)
    try:
        api.get(name)
        msg = 'Snippet copied to clipboard!'
        _success(msg)
    except Exception as e:
        _error(str(e))


@cli.command()
@click.argument('snippets_file', type=click.File('r'), nargs=1)
def install(snippets_file):
    errors = api.install(snippets_file)
    if errors:
        _error('\n'.join(errors))
    else:
        _success('Successfully installed all snippets!')


@cli.command()
def clear():
    api.clear()
    _success('Cleared all snippets!')


@cli.command()
@click.option('-g', '--group', default=None)
def list(group):
    collection = api.get_all(group=group)
    for group in collection.groups():
        click.echo(click.style(group, fg='cyan'))
        for snippet in collection.get_group(group):
            name = _add_tab('Name - {}'.format(snippet.name))
            desc = _add_tab('Description - {}'.format(snippet.description))
            content = _add_tab(snippet.content)
            click.secho(name, fg='red')
            click.secho(desc, fg='green')
            click.secho(content, fg='yellow')
            click.echo('\n')


def _add_tab(text):
    text = '\t' + text
    return text.replace('\n', '\n\t')


def _success(msg):
    click.echo(click.style(msg, fg='green'))


def _error(msg):
    click.echo(click.style(msg, fg='red'))


if __name__ == '__main__':
    cli()
