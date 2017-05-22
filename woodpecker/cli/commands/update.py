import click

from pkg_resources import iter_entry_points
from click_plugins import with_plugins

from woodpecker.sequences.basesequence import BaseSettings


@with_plugins(iter_entry_points('woodpecker.update'))
@click.group(short_help='Updates an entry')
@click.pass_context
def update(ctx):
    """
    Updates the selected entry from the current working directory
    """
    pass


@update.command(short_help='Updates the settings')
@click.pass_context
def settings(ctx):
    """
    Updates the folder settings by merging the actual settings with the 
    required settings from the used sequences
    """

    ###########################################################################
    # Step 1: generate a BaseSettings element
    ###########################################################################
    settings = BaseSettings()

    ###########################################################################
    # Step 2: merge the created settings with all the required settings from
    # the sequences
    ###########################################################################
    # TBD

    ###########################################################################
    # Step 3: Overwrites default data with the existing settings of the user
    # (after validation)
    ###########################################################################
    # TBD
