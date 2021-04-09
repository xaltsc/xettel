
import os
from xettel.base.Zettelkasten import Zettelkasten
import xettel.impl.mmd.ZettelMMD as Z

class ZettelkastenMMD(Zettelkasten):
    @classmethod
    def from_folder(cls, folder):
        ZK = ZettelkastenMMD()
        ZK.folder = folder
        for filepath in os.listdir(ZK.folder):
            if filepath[0] != '.' and filepath not in ["export"]:
                ZK.zettels.append(
                        Z.ZettelMMD.from_file(ZK, filepath)
                        )
        ZK.initialise_rels()
        return ZK
