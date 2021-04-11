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
@click.option('-f', '--force', default=False, is_flag=True, help="force overwriting database",)
@click.option("-1", "--one", help="only update a single file")
@cli.command()
def updatedb(delete, one, force=False):
    if one is not None:
        click.echo("Reading recorded data")
        reader = ZXr.ZXReader(ZK_PATH)
        zk = reader.db_to_zk()
        click.echo("Updating data")
        zk.update_zettel_from_file(one)
        writer = ZXw.ZXWriter(ZK_PATH, zk)
        writer.zk_to_db()
        click.echo("Success !")
    else:
        click.echo("Loading Zettelkasten from files...")
        ZK = Zm.ZettelkastenMMD.from_folder(ZK_PATH) 
        Zwriter = ZXw.ZXWriter(ZK_PATH, ZK)
        click.echo("Recording changes to the database...")
       # click.echo([x.filename for x in ZK[int("2ONQX4RR", 36)].outbound_links])
       # click.echo(ZK[int("2ONRIQW8", 36)].inbound_links)
        Zwriter.zk_to_db(force=force)
        click.echo("Success!")
        if delete:
            Zwriter.delete_in_db()


@cli.command()
@click.option('-e', '--editor', envvar='EDITOR', help="editor to write in")
@click.option('--noeditor', default=False, is_flag=True, help="do not use an editor")
@click.option('--register', default=False, is_flag=True, help="register newly created file")
@click.option('-u', '--returnuid', default=False, is_flag=True, help="return B36 newly created uid (implies --no-editor anf --register)")
@click.option('-t', '--template', help="template for the new file")
@click.argument('name', required=True)
def new(name, editor, template=None, noeditor=False, returnuid=False, register=False):
    if returnuid:
        noeditor = True
        register = True
    template = cfg["Zettelkasten"]["template"] if template == None else template 
    uid = datetime.now().strftime('%y%m%d%H%M%S')
    uid = int36(int(uid))
    path = ZK_PATH + '/' + uid + '-' + name + '.mmd'
    shutil.copyfile(template, path)
    if not noeditor:
        subprocess.run([editor, path])
    if returnuid:
        click.echo(uid)
    else:
        click.echo("New zettel {} created. (Warning: db not updated)".format(uid))
    
    if register:
        reader = ZXr.ZXReader(ZK_PATH)
        zk = reader.db_to_zk()
        zk.update_zettel_from_file(uid + '-' +name + '.mmd')
        writer = ZXw.ZXWriter(ZK_PATH, zk)
        writer.zk_to_db()

@cli.command()
@click.option('-e', '--editor', envvar='EDITOR', help="editor to write in")
@click.argument('identifier', required=True, nargs=-1)
def edit(identifier, editor):
    reader = ZXr.ZXReader(ZK_PATH)
    matches = reader.search(" ".join(identifier))
    if len(matches) == 1:
        doc = matches[0].document
        filename = j.loads(doc.get_data())["filename"]
        path = ZK_PATH + '/' + filename
        subprocess.run([editor, path])
    elif len(matches) == 0: 
        click.echo("No match for identifier")
    else:
        click.echo("This identifier matches too many documents.")


def getter_zettel(z, field):
    if field == "uid":
        return z.get_uid_str()
    elif field == "uid36":
        return z.get_uid_36() 
    elif field == "filename":
        return z.filename
    else:
        try:
            return z.attributes[field]
        except:
            return ""

def getter_match(m, field):
    if field == "uid36":
        return int36(int(m["uid"]))
    else:
        try:
            return m[field]
        except:
            return ""

def __o_map(getter, results):
        mapping = dict(
                [(getter(r, 'uid'), getter(r, 'filename')) for r in results] +
                [(getter(r, 'uid36'), getter(r, 'filename')) for r in results]
                )
        return [j.dumps(mapping)]

def __o_filename(getter, results):
    for r in results:
        yield getter(r, "filename")

def __o_normal(getter, results):
    for r in results:
        tags = getter(r, "tags") 
        title = getter(r, "title")
        abstract = getter(r, "abstract")
        uid36 = getter(r, "uid36")
        form_tags = " ({})".format(tags) if tags != "" else ""
        form_abtr = ": \"{}\"".format(abstract) if abstract != "" else ""
        yield "{}{} -- {}{}".format(uid36,form_tags,title,form_abtr)


output_map = {
        "normal": __o_normal,
        "filename": __o_filename,
        "map": __o_map
        }


@cli.command()
@click.argument('query', nargs=-1, required=True)
@click.option('-o', '--output', type=click.Choice(["normal", "filename", "map"]),default="normal", help="output options",)
@click.option('-a', '--all', default=False, is_flag=True, help="query all")
def search(query, output="normal", all=False):
    reader = ZXr.ZXReader(ZK_PATH)
    if all:
        zk = reader.db_to_zk()
        results = zk
        getter = getter_zettel
    else:
        matches = reader.search(" ".join(query))
        results = map(lambda m: j.loads(m.document.get_data()), matches)
        getter = getter_match

    for line in output_map[output](getter, results):
        click.echo(line)

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
            "--metadata=uid36:{}".format(z.get_uid_36()),
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

