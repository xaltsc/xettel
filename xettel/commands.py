import xettel.impl.mmd.ZettelkastenMMD as Zm
import xettel.zxapian.writer as ZXw

import click

@click.group()
def cli():
    pass

#cli.add_command(updatedb)
#cli.add_command(new)
#cli.add_command(search)
#cli.add_command(show)
#cli.add_command(count)
#cli.add_command(export)


@cli.command()
@click.option('--dir', default="lol", help="Zettelkasten directory")
def updatedb(dir):
    ZK_PATH = dir
    click.echo("Loading Zettelkasten from files...")
    ZK = Zm.ZettelkastenMMD.from_folder(ZK_PATH) 
    Zwriter = ZXw.ZXWriter(ZK_PATH, ZK)
    click.echo("Recording changes to the database...")
    Zwriter.zk_to_db()
    click.echo("Success!")

@cli.command()
def new():
    pass

@cli.command()
def search():
    pass

@cli.command()
def show():
    pass

@cli.command()
def count():
    pass

@cli.command()
def export():
    pass
