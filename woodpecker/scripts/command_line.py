import click

from woodpecker.elements.controller import Controller
from woodpecker.remotes.remotecontroller import RemoteController


@click.group()
@click.version_option()
def main():
    pass


@main.command()
def init():
    print 'init'


@main.command()
def start():
    pass


@main.command()
def remote():
    pass


@main.command()
def harconverter():
    pass


if __name__ == '__main__':
    main()
