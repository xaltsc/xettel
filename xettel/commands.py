import xettel.impl.mmd.ZettelkastenMMD as Zm
import xettel.impl.xapian.ZettelkastenX as Zx
import xettel.zxapian.writer as ZXw
import xettel.zxapian.reader as ZXr

import click
import toml
from datetime import datetime
import subprocess
import json as j
import os
import shutil

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
template_path = None

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
   # click.echo([x.filename for x in ZK[int("2ONQX4RR", 36)].outbound_links])
   # click.echo(ZK[int("2ONRIQW8", 36)].inbound_links)
    Zwriter.zk_to_db(force=True)
    click.echo("Success!")
    if delete:
        Zwriter.delete_in_db()


@cli.command()
@click.option('-e', '--editor', envvar='EDITOR', help="editor to write in")
@click.option('-t', '--template', help="template for the new file")
@click.argument('name', required=True)
def new(name, editor, template=None):
    template = cfg["Zettelkasten"]["template"] if template == None else template 
    uid = datetime.now().strftime('%y%m%d%H%M%S')
    uid = int36(int(uid))
    path = ZK_PATH + '/' + uid + '-' + name + '.mmd'
    shutil.copyfile(template, path)
    subprocess.run([editor, path])
    ZK = Zm.ZettelkastenMMD.from_folder(ZK_PATH) 
    Zwriter = ZXw.ZXWriter(ZK_PATH, ZK)
    Zwriter.zk_to_db()
    click.echo("New zettel {} created.".format(uid))

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
@click.option('-m', '--map', default=False, is_flag=True, help="gives a JSON formatted map UID:Filename")
def search(query, filename=False, map=False):
    reader = ZXr.ZXReader(ZK_PATH)
    matches = reader.search(" ".join(query))
    if map:
        zk = reader.db_to_zk()
        mapping36 = [(z.get_uid_36(), z.filename) for z in zk]
        mapping10 = [(z.get_uid_str(), z.filename) for z in zk]
        mapping = dict(mapping10 + mapping36)
        click.echo(j.dumps(mapping))
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
@click.option('-a', '--action', type=click.Choice(['checkhealth', 'unreachables']), default='checkhealth')
def health(action="checkhealth"):
    ZK = ZXr.ZXReader(ZK_PATH).db_to_zk()
    ZK.build_graph()
    if action == "checkhealth":
        click.echo( "The Zettelkasten is healthy" if ZK.is_healthy() else "The Zettelkasten is not healthy" )
    elif action == "unreachables":
        click.echo("The following files are not reachable from the index.")
        for filename in ZK.unreachable_zettels():
            click.echo(filename)

@cli.command()
@click.argument('query', nargs=-1, required=True)
def count(query):
    reader = ZXr.ZXReader(ZK_PATH)
    matches = reader.search(" ".join(query))
    click.echo(len(list(matches)))


@cli.command()
def export():
    ZK = ZXr.ZXReader(ZK_PATH).db_to_zk()
    for z in ZK:
        file = z.filename
        subprocess.run(["pandoc",
            "--metadata=uid:{}".format(z.get_uid_str()),
            "-F", "/home/ax/docs/90-projects/92-coding/92.08-xettel/pandocfilter.py",
            "-f", "markdown_mmd",
            "-t", "html",
            "-o", ZK_PATH + "/export/" + file[:-4]+".html",
            "--data-dir="+ ZK_PATH + "/export/pandoc/",
            "--shift-heading-level-by" , "1",
            "--template", "zettel",
            ZK_PATH + '/' + file
            ])
        print(file)

