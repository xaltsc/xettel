import impl.mmd.ZettelkastenMMD as Zm
import zxapian.writer as ZXw

import click

@click.command()
@click.option('--dir', default="lol", help="Zettelkasten directory")
def updatedb(dir):
    ZK_PATH = dir
    click.echo("Loading Zettelkasten from files...")
    ZK = Zm.ZettelkastenMMD.from_folder(ZK_PATH) 
    Zwriter = ZXw.ZXWriter(ZK_PATH, ZK)
    click.echo("Recording changes to the database...")
    Zwriter.zk_to_db()
    click.echo("Success!")

@click.command()
def new():
    pass

@click.command()
def search():
    pass

@click.command()
def show():
    pass

@click.command()
def count():
    pass

@click.command()
def export():
    pass
