
#import Zettelkasten as ZK
import os
import pymmd.mmd as mmd
import subprocess
import xapian
import ZettelXapian as ZX
import hashlib

class Zettel:
    "A single Zettel"

    def __init__(self, parent, uid, filename):
        self.parent = parent
        self.__uid = uid
        self.filename = filename 
        self.attributes = {}
        self.__hash = ""
        self.outbound_links = []
        self.inbound_links = []

    def set_attributes_from_file(self):
        self.attributes = {}

    def set_outbound_links_from_file(self):
        self.outbound_links = []

    def set_inbound_links(self):
        for z in self.parent:
            if self in z.outbound_links:
                self.inbound_links.append(z)

    def get_uid(self):
        return self.__uid

    def create_hash(self, tobehashed):
        h = hashlib.new('sha3_224')
        h.update(self.filename.encode('utf-8'))
        h.update(tobehashed.encode('utf-8'))
        self.__hash = h.hexdigest()

    def get_hash(self):
        return self.__hash

    def get_uid_str(self):
        return str(self.__uid).rjust(12, "0")

    def to_xapian(self, indexer):
        document = xapian.Document()
        indexer.set_document(document)

        self.set_inbound_links()

        for link in self.inbound_links:
            indexer.index_text(link.get_uid_str(), 1, "LI")

        for link in self.outbound_links:
            indexer.index_text(link.get_uid_str(), 1, "LO")

        if "text" in self.attributes:
            document.set_data(self.attributes["text"])

        indexer.index_text(self.filename, 1, "F")
        indexer.index_text(self.get_uid_str(), 1, "Q")
        indexer.index_text(self.get_hash(), 1, "H")
        document.add_boolean_term("Q"+self.get_uid_str())
        document.add_boolean_term("H"+self.get_hash())
        document.add_boolean_term("F"+self.filename)

        #indexer.index_text(self.attributes[title])
        #indexer.increase_termpos()
        #indexer.index_text(self.attributes[text])

        for key in self.attributes.keys():
            prefix = ZX.attributes_dict[key]
            indexer.index_text(self.attributes[key], 1, prefix)

        return document

    @classmethod
    def from_file(cls, parent, filename):
        uid = filename.split("-")[0]
        if len(uid)==8:
            uid = int(uid, base=36)
        elif len(uid)==12:
            uid = int(uid)
        else:
            raise ValueError("UID {0} is not valid".format(uid))
        z = Zettel(
                parent,
                uid,
                filename
                )
        return z

    @classmethod
    def from_xapian(cls, parent, doc):
        print(doc.get_data())


class ZettelMMD(Zettel):

    @classmethod
    def from_file(cls, parent, filename):
        z = super().from_file(parent,filename)
        zmmd = ZettelMMD(parent, z.get_uid(), filename)
        zmmd.set_outbound_links_from_file()
        zmmd.set_attributes_from_file()
        return zmmd


    def set_outbound_links_from_file(self):
        filepath = self.parent.folder +'/'+self.filename
        fp = os.path.realpath(filepath)
        link_output = subprocess.run([
            '/home/ax/docs/90-projects/92-coding/92.08-xettel/getlinks.hs',
            fp], stdout=subprocess.PIPE)
        
        link_list = link_output.stdout.decode('utf-8').split(' ')
        if link_list == ['']:
            return []
        raw_ob_links = map(int, link_list)
        self.outbound_links = [ self.parent[link] for link in raw_ob_links if link in self.parent ]

    def set_attributes_from_file(self):
        filepath = self.parent.folder +'/'+self.filename
        fp = os.path.realpath(filepath)

        with open(fp) as f:
            mmdfile = f.read()

        self.create_hash(mmdfile)

        for key in mmd.keys(mmdfile):
            self.attributes[key]=mmd.value(mmdfile, key)

        text = "\n".join(mmdfile.split("\n\n")[1:])
        self.attributes["text"] = text 


    def to_xapian(self, indexer):
        self.set_outbound_links_from_file()
        return super().to_xapian(indexer)

