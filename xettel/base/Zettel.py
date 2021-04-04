
#import Zettelkasten as ZK

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

