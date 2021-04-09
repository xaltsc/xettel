#!/bin/env python 

import toml

from pandocfilters import Str, Link, toJSONFilters, toJSONFilter
import xettel.zxapian.reader as ZXr
from xettel.zxapian.resources import int36

cfg = None
ZK_PATH = None

def cfgparse(configpath):
    return toml.load(configpath)


cfg = cfgparse("/home/ax/.config/xettel.toml")
ZK_PATH = cfg["Zettelkasten"]["directory"]
reader = ZXr.ZXReader(ZK_PATH)
zk = reader.db_to_zk()

def fetch_backlinks(key, value, format, meta):
   if "uid" not in meta.keys() or "backlinks" in meta.keys():
       return
   struid = meta["uid"]["c"]

   if len(struid) == 8:
       uid = int(struid, base=36)
   elif len(struid) == 12:
       uid = int(struid)

   backlinks = zk[uid].inbound_links
   
   backlinksJSON = []
   for bl in backlinks:
       fn = bl.filename[:-4] + ".html"
       name = "-".join(bl.filename[:-4].split("-")[1:])
       backlinksJSON.append({ "t": "MetaInlines", "c":[
           Link(("", ["backlink"], []), [Str(name)], (fn, name))
           ]})
   meta["backlinks"] = {"t": "MetaList", "c": backlinksJSON}


def arraify_tags(key, value, format, meta):
    if "tags" not in meta.keys():
        return
    tags = meta["tags"]
    if tags["t"] == "MetaBlocks":
        tags["t"] = "MetaList"
        effective_tags = tags["c"][0]["c"]
        return_tags = []
        for elt in effective_tags:
            if "c" in elt.keys():
                return_tags.append({ "t": "MetaInlines", "c":[{
                    "t": "Str", "c": elt["c"]
                    }] })
        tags["c"] = return_tags 
 
def convert_links(key, value, format, meta):
    if key == "Str":
        if len(value)==12 and value[:2]=='[[' and value[-2:]==']]':
            address = value[2:-2]
            uid = int(address, base=36)
            filename = zk[uid].filename
            title = filename[:-4]
            filename = title + ".html"
            title="-".join(title.split("-")[1:])
            return Link(("", ["zettel.link"], []), [Str(address)], (filename, title))
        elif len(value)==18 and value[:2]=='[[' and value[-2:]==']]':
            address = int(value[2:-2])
            uid = address
            filename = zk[uid].filename
            title = filename[:-4]
            filename = title + ".html"
            title="-".join(title.split("-")[1:])
            return Link(("", ["zettel.link"], []), [Str(address)], (filename, title))

        #    return Str("DEC")
def pandocfilter(key, value, format, meta):
    fetch_backlinks(key,value,format,meta)
    arraify_tags(key,value,format,meta)
    return convert_links(key, value, format, meta)

        
if __name__ == "__main__":
    toJSONFilter(pandocfilter)
