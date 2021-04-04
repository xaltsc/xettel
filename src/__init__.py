#!/bin/env python3

import click
from subcommands import *

@click.group()
def cli():
    pass

cli.add_command(updatedb)
cli.add_command(new)
cli.add_command(search)
cli.add_command(show)
cli.add_command(count)
cli.add_command(export)

if __name__ == '__main__':
    cli()
