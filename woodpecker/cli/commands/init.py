import click
import os
import shutil

from woodpecker.sequences.basesequence import BaseSettings


@click.command(short_help='Initialize a folder')
@click.option('--force', is_flag=True,
              help='Forces the initialization of a folder. '
                   'Existing subfolders will be overwritten.')
@click.pass_context
def init(ctx, force):
    """
    Initialize a folder for usage with Woodpecker.
    If an existing installation is found, returns an error 
    """

    workdir = os.path.abspath(ctx.obj['WORKDIR'])
    click.echo(
        'Initializing working directory {workdir}'.format(workdir=workdir)
    )

    ###########################################################################
    # Step 1: check for folder existence, if they are not found create them
    ###########################################################################
    folders = (
        'results',      # Folder containing the results of the executions
        'sequences',    # Folder containing the recorder sequences
        'config',       # Fonder containing the different profiles
        'resources',    # Folder containing data for parameters
        'scenarios',    # Folder containing the scenario(s) for the test
    )
    for folder in folders:
        folder_complete_path = os.path.join(workdir, folder)
        if os.path.isdir(folder_complete_path):
            if force:
                shutil.rmtree(folder_complete_path)
            else:
                raise click.ClickException(
                    'Folder "{folder}" already exists inside working '
                    'directory, aborting. To avoid this error, '
                    'use the init command with the --force option'.format(
                        folder=folder_complete_path
                    )
                )
        click.echo(
            'Creating folder {folder}... '.format(folder=folder), nl=False
        )
        os.mkdir(folder_complete_path)
        click.echo('OK')

    ###########################################################################
    # Step 2: insert default config file
    ###########################################################################
    default_config_path = os.path.join(workdir, 'config', 'default.cfg')
    _rmfile_with_error(default_config_path, force)

    # Instantiate the base settings class
    click.echo('Creating default config file... ', nl=False)
    default_settings = BaseSettings(indent_type=None)

    # Override the filename, to enable writing on file
    default_settings.filename = default_config_path
    default_settings.indent_type = ''

    # Create the file
    default_settings.write()
    click.echo('OK')

    ###########################################################################
    # Step 3: create empty scenario file
    ###########################################################################
    default_scenario_path = os.path.join(workdir, 'scenarios', 'default.cfg')
    _rmfile_with_error(default_scenario_path, force)

    # Touch the file
    click.echo('Creating default scenario... ', nl=False)
    open(default_scenario_path, 'a').close()
    click.echo('OK')


def _rmfile_with_error(file_path, forced=False):
    if os.path.isfile(file_path):
        if forced:
            os.remove(file_path)
        else:
            raise click.ClickException(
                'File {filename} already exists inside working directory, '
                'aborting. To avoid this error, '
                'use the init command with the --force option'.format(
                    filename=file_path
                )
            )
