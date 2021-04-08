
import xettel.base.Zettel as Z
import os
import xapian
import networkx as nx

class Zettelkasten:
    "A list of Zettels"
    def __init__(self):
        self.folder = ""
        self.zettels = []
        self.graph = None

    @classmethod
    def from_folder(cls, folder):
        ZK = Zettelkasten()
        ZK.folder = folder
        for filepath in os.listdir(ZK.folder):
            if filepath[0] != '.':
                ZK.zettels.append(
                        Z.Zettel.from_file(ZK, filepath)
                        )
        ZK.initialise_rels()
        return ZK

    def initialise_rels(self):
        for z in self:
            z.set_pre_all()
        for z in self:
            z.set_all()

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
        
    # Health checks {{{

    def build_graph(self):
        self.initialise_rels()
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(self.zettels)
        for z in self:
            for zo in z.outbound_links:
                self.graph.add_edge(z, zo)

    def is_healthy(self):
        return nx.is_weakly_connected(self.graph)

    def unreachable_zettels(self):
        source = self[0]
        components = nx.weakly_connected_components(self.graph)
        main_comp = [ comp for comp in components if source in comp ][0]
        fns = [ z.filename for z in self if z not in main_comp ]
        return fns
    
    def display_graph(self):
        nx.draw_networkx_labels(self.graph, pos=nx.spring_layout(self.graph), labels=dict([(z, z.filename) for z in ZK]))

   # }}}
    



