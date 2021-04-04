import xapian
import xettel.base.Zettelkasten as ZK
import xettel.base.Zettel as Z
from xettel.zxapian.basic import ZX

class ZXReader(ZX):

    def __init__(self, folder):
        self.folder = folder
        self.db = xapian.Database(self.folder + '/.xetteldb')
        super().__init__(folder, db=self.db)

    def db_to_zk(self):
        retZK = ZK.Zettelkasten()
        retZK.folder = self.folder

        for i in range(1,self.db.get_lastdocid() + 1):
            try:
                doc = self.db.get_document(i)
                z = Z.Zettel.from_xapian(retZK, doc, i)
                retZK.zettels.append(z)
            except xapian.DocNotFoundError:
                pass

        return retZK

