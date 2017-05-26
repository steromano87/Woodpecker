import click
import click_shell

from pkg_resources import iter_entry_points
from click_plugins import with_plugins

from .._version import get_versions

from .commands.init import init
from .commands.update import update
from commands.generate import generate


@with_plugins(iter_entry_points('woodpecker.main'))
@click_shell.shell(prompt='Woodpecker > ',
                   intro='Starting Woodpecker in interactive mode...')
@click.version_option(version=get_versions()['version'],
                      prog_name='Woodpecker',
                      message='%(prog)s %(version)s')
@click.option('--workdir', '-d', default='.',
              type=click.Path(),
              help='Target directory (defaults to current directory)')
@click.pass_context
def woodpecker(ctx, workdir):
    """
    Lightweight, Python based load test tool 
    """
    ctx.obj['WORKDIR'] = workdir

woodpecker.add_command(init)
woodpecker.add_command(update)
woodpecker.add_command(generate)


if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    woodpecker(obj={})
