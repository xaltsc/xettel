import xettel.impl.mmd.ZettelkastenMMD as Zm
import xettel.zxapian.writer as ZXw

import click
import toml
from datetime import datetime
import subprocess

def cfgparse(configpath):
    return toml.load(configpath)

def int36(num):
    digits="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base36=""
    if num == 0:
        return "0"
    while num != 0:
        base36 = digits[num % 36] + base36
        num = num // 36
    return base36

ZK_PATH = None
cfg = None

@click.group()
@click.option('-c', '--config', default="/home/ax/.config/xettel.toml", help="config file")
@click.option('-d', '--dir', help="Zettelkasten directory")
def cli(config, dir):
    global cfg
    global ZK_PATH

    cfg = cfgparse(config)
    ZK_PATH = cfg["Zettelkasten"]["directory"] if dir == None else dir
    pass

@click.option('-x', '--delete', default=False, is_flag=True, help="purge database of files not present anymore",)
@cli.command()
def updatedb(delete):
    click.echo("Loading Zettelkasten from files...")
    ZK = Zm.ZettelkastenMMD.from_folder(ZK_PATH) 
    Zwriter = ZXw.ZXWriter(ZK_PATH, ZK)
    click.echo("Recording changes to the database...")
    Zwriter.zk_to_db()
    click.echo("Success!")
    if delete:
        Zwriter.delete_in_db()


@cli.command()
@click.option('-n', '--name', help="name of the Zettel")
def new(name):
    uid = datetime.now().strftime('%y%m%d%H%M%S')
    uid = int36(int(uid))
    path = ZK_PATH + '/' + uid + '-' + name + '.mmd'
    subprocess.run(['vim', path])
    ZK = Zm.ZettelkastenMMD.from_folder(ZK_PATH) 
    Zwriter = ZXw.ZXWriter(ZK_PATH, ZK)
    Zwriter.zk_to_db()

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
