
import pymmd.mmd as mmd
import os
import subprocess

from xettel.base.Zettel import Zettel

class ZettelMMD(Zettel):

    @classmethod
    def from_file(cls, parent, filename):
        z = super().from_file(parent,filename)
        zmmd = ZettelMMD(parent, z.get_uid(), filename)
        zmmd.set_outbound_links()
        zmmd.set_attributes()
        return zmmd


    def set_outbound_links(self):
        filepath = self.parent.folder +'/'+self.filename
        fp = os.path.realpath(filepath)
        link_output = subprocess.run([
            '/home/ax/docs/90-projects/92-coding/92.08-xettel/getlinks.hs',
            fp], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        link_list = link_output.stdout.decode('utf-8').split(' ')
        if link_list == ['']:
            return []
        raw_ob_links = map(int, link_list)
        self.outbound_links = [ self.parent[link] for link in raw_ob_links if link in self.parent ]

    def set_attributes(self):
        filepath = self.parent.folder +'/'+self.filename
        fp = os.path.realpath(filepath)

        with open(fp) as f:
            mmdfile = f.read()

        self.create_hash(mmdfile)

        for key in mmd.keys(mmdfile):
            self.attributes[key]=mmd.value(mmdfile, key)

        text = "\n".join(mmdfile.split("\n\n")[1:])
        self.attributes["text"] = text 
