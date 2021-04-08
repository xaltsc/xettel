
from xettel.base.Zettel import Zettel
import json as j

class ZettelX(Zettel):

    def __init__(self, parent, doc, id):
        data = j.loads(doc.get_data())
        super().__init__(parent, int(data["uid"]),
                         data["filename"])
        self.__xdata = data
        self.__hash = data["hash"]
        self.__outbound_links_uids = data["links"]
        self.__inbound_links_uids = data["backlinks"]
        self.__xapian_id = id

    def set_attributes(self):
        keys_to_look = list(self.__xdata.keys())
        ignorekeys=["filename", "hash", "uid", "links", "backlinks"]
        for key in ignorekeys:
            if key in keys_to_look:
                keys_to_look.remove(key)
        
        for key in keys_to_look:
            self.attributes[key] = self.__xdata[key]


    def set_outbound_links(self):
        for link in self.__outbound_links_uids:
            try:
               self.outbound_links.append(self.parent[int(link)])
            except IndexError as e:
                print(e)

    def set_inbound_links(self):
        """ Result should be equal to inbound links determied with parenth
        """
        for link in self.__inbound_links_uids:
            try:
                self.inbound_links.append(self.parent[int(link)])
            except IndexError as e:
                print(e)

    def __hash__(self):
        return int(self.__hash, base=16)
