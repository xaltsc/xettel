
from xettel.base.Zettelkasten import Zettelkasten
import xettel.impl.xapian.ZettelX as Z
import xapian

class ZettelkastenX(Zettelkasten):

    @classmethod
    def from_xapian(cls, db, folder):
        ZK = ZettelkastenX()
        ZK.folder = folder
        maxID = db.get_lastdocid()+1
        for i in range(1, maxID):
            try:
                doc = db.get_document(i)
                z = Z.ZettelX(ZK, doc, i)
                ZK.zettels.append(z)
            except xapian.DocNotFoundError:
                pass

        ZK.initialise_rels()
        return ZK
