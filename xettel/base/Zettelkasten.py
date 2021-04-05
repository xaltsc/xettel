
import xettel.base.Zettel as Z
import os
import xapian
import networkx as nx

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
                        Z.Zettel.from_file(ZK, filepath)
                        )
        return ZK

    def indices(self):
        for z in self:
            yield z.get_uid()

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

    def to_xapian(self):
        return self.__iter__()
        
    @classmethod
    def from_xapian(cls, db, folder):
        ZK = Zettelkasten()
        ZK.folder = folder

        maxID = db.get_lastdocid()
        for i in range(1, maxID):
            try:
                doc = db.get_document(i)
                ZK.zettels.append(Zettel.from_xapian(ZK, doc))
            except xapian.DocNotFoundError:
                pass
        return ZK
    
    def check_health(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.zettels)
        for z in self:
            for zo in z.outbound_links:
                G.add_edge(z, zo)

        return nx.is_weakly_connected(G)


