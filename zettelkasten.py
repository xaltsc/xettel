#!/usr/bin/env python

import xapian
import os
import subprocess

def get_outbound_liks_from_file(filepath):
    fp = os.path.realpath(filepath)
    link_output = subprocess.run([
        '/home/ax/docs/90-projects/92-coding/92.08-bokz/getlinks.hs',
        fp], stdout=subprocess.PIPE)
    
    link_list = link_output.stdout.decode('utf-8').split(' ')
    if link_list == ['']:
        return []
    else:
        return list(map(int, link_list))

class Zettelkasten:
    "A list of Zettels"
    def __init__(self):
        self.folder = ""
        self.zettels = []

    @classmethod
    def from_folder(cls, folder):
        ZK = Zettelkasten()
        ZK.folder = folder
        for filepath in os.listdir(ZK.folder):
            if filepath[0] != '.':
                ZK.zettels.append(
                        Zettel.from_file(ZK, filepath)
                        )
        return ZK

    def __iter__(self):
        return self.zettels.__iter__()
    
    def __contains__(self, y):
        for z in self:
            if z.get_uid() == y:
                return True
        return False

    def __getitem__(self, y):
        for z in self:
            if z.get_uid() == y:
                return z
        raise IndexError("No Zettel with such UID: {0}".format(y))



class Zettel:
    "A single Zettel"

    def __init__(self, parent, uid, filename):
        self.parent = parent
        self.__uid = uid
        self.filename = filename 
        self.attributes = {} 
        self.outbound_links = []
        self.inbound_links = []

    def set_attributes_from_file(self, folder):
        return {}

    def set_outbound_links_from_file(self):
        outlinks = get_outbound_liks_from_file(self.parent.folder +'/'+self.filename)
        self.outbound_links = [ self.parent[link] for link in outlinks if link in self.parent ]
        

    def get_uid(self):
        return self.__uid

    @classmethod
    def from_file(cls, parent, filename):
        uid = filename.split("-")[0]
        if len(uid)==8:
            uid = int(uid, base=36)
        else:
            uid = int(uid)
        z = Zettel(
                parent,
                uid,
                filename
                )
        z.set_attributes_from_file(parent.folder)
        return z




DB_PATH="/home/ax/docs/20-work/22-know-and-org/22.01-zk/.bokzdb"

try:
    print("lol")
#    db = xapian.WriteableDatable(DB_PATH, xapian.DB_CREATE_OR_OPEN)

#    indexer = xapian.TermGenerator()

#    for file in 
#        doc = xapian.Document()
#        doc.set_data()
#
#        indexer.set_document(doc)
#        db.add_document(doc)
except Exception as e:
    print("Exception: %s" % str(e), file=sys.stderr)
    sys.exit(1)
