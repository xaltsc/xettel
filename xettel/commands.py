import xettel.impl.mmd.ZettelkastenMMD as Zm
import xettel.zxapian.writer as ZXw
import xettel.zxapian.reader as ZXr

import click
import toml
from datetime import datetime
import subprocess
import json as j

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
    if not ZK.check_health():
        click.echo("Warning: the Zettelkasten is not connected.")
    if delete:
        Zwriter.delete_in_db()


@cli.command()
@click.option('-e', '--editor', envvar='EDITOR', help="editor to write in")
@click.argument('name', required=True)
def new(name, editor):
    uid = datetime.now().strftime('%y%m%d%H%M%S')
    uid = int36(int(uid))
    path = ZK_PATH + '/' + uid + '-' + name + '.mmd'
    subprocess.run([editor, path])
    ZK = Zm.ZettelkastenMMD.from_folder(ZK_PATH) 
    Zwriter = ZXw.ZXWriter(ZK_PATH, ZK)
    Zwriter.zk_to_db()

@cli.command()
@click.option('-e', '--editor', envvar='EDITOR', help="editor to write in")
@click.argument('identifier', required=True)
def edit(identifier, editor):
    reader = ZXr.ZXReader(ZK_PATH)
    matches = reader.search(" ".join(identifier))
    if len(list(matches)) == 1:
        doc = list(matches)[0].document
        path = ZK_PATH + '/' + doc.filename
        subprocess.run([editor, path])
        ZK = Zm.ZettelkastenMMD.from_folder(ZK_PATH) 
        Zwriter = ZXw.ZXWriter(ZK_PATH, ZK)
        Zwriter.zk_to_db()
    elif len(list(matches)) == 0: 
        click.echo("No match for identifier")
    else:
        click.echo("This identifier matches too many documents.")

@cli.command()
@click.argument('query', nargs=-1, required=True)
@click.option('-f', '--filename', default=False, is_flag=True, help="output only filename",)
def search(query, filename=False):
    reader = ZXr.ZXReader(ZK_PATH)
    matches = reader.search(" ".join(query))
    for match in matches:
        fields = j.loads(match.document.get_data())
        if filename:
            buildshownmatch = fields["filename"]
        else:
            buildshownmatch="{}".format(int36(int(fields["uid"])))
            if "tags" in fields:
                buildshownmatch+= " ({})".format(fields["tags"])
            buildshownmatch += " -- {}".format(fields["title"])
            if "abstract" in fields:
                buildshownmatch+= " : \"{}\"".format(fields["abstract"])
        click.echo(buildshownmatch)

@cli.command()
@click.argument('query', nargs=-1, required=True)
def count(query):
    reader = ZXr.ZXReader(ZK_PATH)
    matches = reader.search(" ".join(query))
    click.echo(len(list(matches)))


@cli.command()
def export():
    pass
