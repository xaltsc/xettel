
import os
from base.Zettelkasten import Zettelkasten
import ZettelMMD as Z

class ZettelkastenMMD(Zettelkasten):
    @classmethod
    def from_folder(cls, folder):
        ZK = ZettelkastenMMD()
        ZK.folder = folder
        for filepath in os.listdir(ZK.folder):
            if filepath[0] != '.':
                ZK.zettels.append(
                        Z.ZettelMMD.from_file(ZK, filepath)
                        )
        return ZK
