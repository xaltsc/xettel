
import subprocess
from pandocfilters import walk, Space, Str, stringify
import json as j

def getJSON(filepath):
    return subprocess.run(["pandoc",
        "-f", "markdown_mmd",
        "-t", "json",
        filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL).stdout.decode('utf-8')

def extractLinks(key, value, format, meta):
    if key not in ["Str", "Code"]:
        return
    if len(value)==12 and value[:2]=='[[' and value[-2:]==']]':
        address = value[2:-2]
        uid = int(address, base=36)
        return Str(str(uid))
    elif len(value)==18 and value[:2]=='[[' and value[-2:]==']]':
        address = int(value[2:-2])
        uid = address
        return(Str(uid))
    else:
        return Space()


def getLinks(filepath):
    jsonfile = j.loads(getJSON(filepath))
    #print(filepath)
    #print(jsonfile["blocks"])
    altered = walk(jsonfile, extractLinks, "", {})
    result = stringify(altered).split()
    #print(result)
    return [x for x in result if x.isdecimal()] 
