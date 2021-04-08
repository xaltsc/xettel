
#import Zettelkasten as ZK

import xapian
import xettel.zxapian.resources as zxr 
import hashlib
import json as j

class Zettel:
    "A single Zettel"

# Constructors {{{

    def __init__(self, parent, uid, filename):
        self.parent = parent
        self.__uid = uid
        self.filename = filename 
        self.attributes = {}
        self.__hash = "" 
        self.__outbound_links_uids = []
        self.__inbound_links_uids = []
        self.outbound_links = []
        self.inbound_links = []

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

# }}}

# A posteriori setting once the ZK is complete {{{

    def set_pre_all(self):
        self.set_outbound_links()

    def set_all(self):
        self.set_attributes()
        self.set_inbound_links()

    def set_attributes(self):
        self.attributes = {}

    def set_outbound_links(self):
        self.outbound_links = []

    def set_inbound_links(self):
        for z in self.parent:
            if self in z.outbound_links:
                self.inbound_links.append(z)


#}}}

# Getters {{{
    
    def get_uid(self):
        return self.__uid
 
    def get_uid_36(self):
        return zxr.int36(self.__uid)

    def create_hash(self, tobehashed):
        h = hashlib.new('sha3_224')
        h.update(self.filename.encode('utf-8'))
        h.update(tobehashed.encode('utf-8'))
        self.__hash = h.hexdigest()

    def get_hash(self):
        return self.__hash

    def get_uid_str(self):
        return str(self.__uid).rjust(12, "0")
# }}}
    
    # Export to database {{{
    def to_xapian(self, indexer):
        document = xapian.Document()
        indexer.set_document(document)

        # Set data {{{
        data = {}

        
        data["uid"] = self.get_uid()
        data["filename"] = self.filename
        data["backlinks"] = [ x.get_uid() for x  in self.inbound_links]
        data["links"] = [ x.get_uid() for x  in self.outbound_links]
        data["hash"] = self.get_hash()

        if "tags" in self.attributes:
            data["tags"] = self.attributes["tags"]

        if "title" in self.attributes:
            data["title"] = self.attributes["title"]
        else:
            tilewithext="-".join(self.filename.split('-')[1:])
            title= ".".join(tilewithext.split('.')[:-1])
            data["title"] = title

        if "abstract" in self.attributes:
            data["abstract"]=self.attributes["abstract"]


        document.set_data(j.dumps(data))
        # }}}

        # Set indexed terms {{{
        indexer.index_text(self.get_uid_str(), 1, "Q")
        indexer.index_text(self.get_uid_36(), 1, "Q")

        indexer.index_text(self.filename, 1, "F")
        indexer.index_text(self.get_hash(), 1, "H")

        document.add_boolean_term("Q"+self.get_uid_str())
        document.add_boolean_term("Q"+self.get_uid_36())
        document.add_boolean_term("H"+self.get_hash())
        document.add_boolean_term("F"+self.filename)

        for link in self.inbound_links:
            document.add_boolean_term("LI"+link.get_uid_str())
            document.add_boolean_term("LI"+link.get_uid_36())
            indexer.index_text(link.get_uid_str(), 1, "LI")
            indexer.index_text(link.get_uid_36(), 1, "LI")

        for link in self.outbound_links:
            document.add_boolean_term("LO"+link.get_uid_str())
            document.add_boolean_term("LO"+link.get_uid_36())
            indexer.index_text(link.get_uid_str(), 1, "LO")
            indexer.index_text(link.get_uid_36(), 1, "LO")

        for key in self.attributes.keys():
            prefix = zxr.attributes_dict[key]
            indexer.index_text(self.attributes[key], 1, prefix)

        # }}}

        return document

    #}}}

    
    def __hash__(self):
        if type(self.__hash) == str:
            return int(self.__hash, base=16)
        else:
            return self.__hash
