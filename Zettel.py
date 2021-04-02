
#import Zettelkasten as ZK
import os

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
        filepath = self.parent.folder +'/'+self.filename
        fp = os.path.realpath(filepath)
        link_output = subprocess.run([
            '/home/ax/docs/90-projects/92-coding/92.08-bokz/getlinks.hs',
            fp], stdout=subprocess.PIPE)
        
        link_list = link_output.stdout.decode('utf-8').split(' ')
        if link_list == ['']:
            return []
        raw_ob_links = map(int, link_list)
        self.outbound_links = [ self.parent[link] for link in outlinks if link in self.parent ]

    def set_inbound_links(self):
        for z in self.parent:
            if self in z.outbound_links:
                self.inbound_links.append(z)
        

    def get_uid(self):
        return self.__uid

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
        z.set_attributes_from_file(parent.folder)
        return z
