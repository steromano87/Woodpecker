import click

from pkg_resources import iter_entry_points
from click_plugins import with_plugins


@with_plugins(iter_entry_points('woodpecker.generate'))
@click.group(short_help='Creates a new entry')
@click.pass_context
def generate(ctx):
    """
    Generates a new Woodpecker item in the proper folder
    """
    pass


@with_plugins(iter_entry_points('woodpecker.generate.sequence'))
@generate.group(short_help='Generates a new sequence')
@click.option('--name', '-f', help='Name of the sequence to be generated')
@click.option('--file', '-f',
              type=click.Path(exists=False, dir_okay=True, writable=True),
              help='Name of the file that contains the generated sequence. '
                   'If no name is provided, the file will be named after the '
                   'sequence name and will be placed under the default '
                   '"sequences" folder.',
              default=None)
@click.pass_context
def sequence(ctx, name, file):
    """
    Generates a new sequence from the given source.
    If the sequence type is provided, all the required include statements 
    will be automatically added, else the type of the sequence will be 
    determined by the issued command
    """
    ctx.obj['SEQUENCE_NAME'] = name or 'NewSequence'
    ctx.obj['SEQUENCE_FILE'] = file or ''.join(
        (
            ctx.obj['WORKDIR'],
            '/sequences/',
            ctx.obj['SEQUENCE_NAME'],
            'py')
    )


@sequence.command(short_help='Generates a new, empty sequence')
@click.option('--type', '-t',
              help='Sequence class to be used',
              type=(str, str),
              default=(None, None),
              metavar='<MODULE> <CLASS>')
@click.pass_context
def from_scratch(ctx, type):
    """
    Generates a new, empty sequence.
    If the sequence type is provided, all the required include statements 
    will be automatically added, else a BaseSequence will be created
    """
    pass


@sequence.command(short_help='Generates a new sequence from HAR files')
@click.argument('har_files', type=click.File('r'), nargs=-1)
@click.pass_context
def from_har(ctx, har_files):
    """
    Generates a new sequence (HttpSequence) from one or more HAR files
    """
    pass


@sequence.command(short_help='Generates a new sequence from SAZ files')
@click.argument('saz_files', type=click.File('r'), nargs=-1)
@click.pass_context
def from_saz(ctx, saz_files):
    """
    Generates a new sequence (HttpSequence) from one or more SAZ files
    """
    pass
