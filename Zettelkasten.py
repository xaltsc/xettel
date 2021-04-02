
import Zettel as Z
import os

class Zettelkasten:
    "A list of Zettels"
    def __init__(self):
        self.folder = ""
        self.zettels = []

    @classmethod
    def from_folder(cls, folder,):
        ZK = Zettelkasten()
        ZK.folder = folder
        for filepath in os.listdir(ZK.folder):
            if filepath[0] != '.':
                ZK.zettels.append(
                        Z.Zettel.from_file(ZK, filepath)
                        )
        return ZK

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


class ZettelkastenMMD(Zettelkasten):
    @classmethod
    def from_folder(cls, folder,):
        ZK = ZettelkastenMMD()
        ZK.folder = folder
        for filepath in os.listdir(ZK.folder):
            if filepath[0] != '.':
                ZK.zettels.append(
                        Z.ZettelMMD.from_file(ZK, filepath)
                        )
        return ZK

