
#import Zettelkasten as ZK

import xapian
import xettel.zxapian.resources as zxr 
import hashlib
import json as j

class Zettel:
    "A single Zettel"

    def __init__(self, parent, uid, filename, xid=None, xterms=None):
        self.parent = parent
        self.__uid = uid
        self.__xapian_id = xid
        self.__xapian_terms = xterms
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

        data = {}
        data["uid"]=self.get_uid_str()
        if "tags" in self.attributes:
            tagstring=" ".join(map(lambda x: '#'+x, self.attributes["tags"].split(",")))
            data["tags"]=tagstring

        if "title" in self.attributes:
            data["title"] = self.attributes["title"]
        else:
            tilewithext="-".join(self.filename.split('-')[1:])
            title= ".".join(tilewithext.split('.')[:-1])
            data["title"] = title

        if "abstract" in self.attributes:
            data["abstract"]=self.attributes["abstract"]


        document.set_data(j.dumps(data))

        indexer.index_text(self.filename, 1, "F")
        indexer.index_text(self.get_uid_str(), 1, "Q")
        indexer.index_text(self.get_hash(), 1, "H")
        document.add_boolean_term("Q"+self.get_uid_str())
        document.add_boolean_term("H"+self.get_hash())
        document.add_boolean_term("F"+self.filename)

        for key in self.attributes.keys():
            prefix = zxr.attributes_dict[key]
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
    def from_xapian(cls, parent, doc, id):
        terms = zxr.dict_from_termlist(doc.termlist())

        uid = int(terms["uid"][0])

        filename = ""
        for f in terms["filename"]:
            if len(f)>len(filename):
                filename = f

        z = Zettel(
                parent,
                uid,
                filename,
                xid=id,
                xterms=terms
                )
        return z

    def set_attributes_from_xapian(self):
        self.__hash = self.__xapian_terms["hash"]

        keys_to_look = list(self.__xapian_terms.keys())
        ignorekeys=["filename", "hash", "uid", "links", "backlinks"]
        for key in ignorekeys:
            if key in keys_to_look:
                keys_to_look.remove(key)
        
        for key in keys_to_look:
            self.attributes[key] = self.__xapian_terms[key]

    def set_outbound_links_from_xapian(self):
        if "links" in self.__xapian_terms.keys():
            for link in self.__xapian_terms["links"]:
                try:
                   self.outbound_links.append(self.parent[int(link)])
                except IndexError as e:
                    print(e)

    def set_inbound_links_from_xapian(self):
        """ Result should be equal to inbound links determied with parenth
        """
        if "backlinks" in self.__xapian_terms.keys():
            for link in self.__xapian_terms["backlinks"]:
                try:
                    self.inbound_links.append(self.parent[int(link)])
                except IndexError as e:
                    print(e)
