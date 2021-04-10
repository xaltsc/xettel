
import os

import pymmd.mmd as mmd

from xettel.base.Zettel import Zettel
from xettel.impl.mmd.resources import getLinks

import click

class ZettelMMD(Zettel):

    @classmethod
    def from_file(cls, parent, filename):
        z = super().from_file(parent,filename)
        zmmd = ZettelMMD(parent, z.get_uid(), filename)
        return zmmd


    def set_outbound_links(self):
        filepath = self.parent.folder +'/'+self.filename
        fp = os.path.realpath(filepath)
        
        self.outbound_links = [] 
        for link in getLinks(filepath):
            try:
                self.outbound_links.append(self.parent[int(link)])
            except IndexError:
                click.echo(
                "UID {0} link in file {1} points nowhere"
                .format(link, filepath),
                err=True)

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
