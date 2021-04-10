import xapian
import xettel.impl.xapian.ZettelkastenX as ZKX
from xettel.zxapian.basic import ZX

class ZXReader(ZX):

    def __init__(self, folder):
        self.folder = folder
        self.db = xapian.Database(self.folder + '/.xetteldb')
        super().__init__(folder, db=self.db)

    def db_to_zk(self):
        return ZKX.ZettelkastenX.from_xapian(self.db, self.folder)

    def search(self, querystring):
        # Do not set wildcard, prevents query fro, being properly parsed
        query = self.qp.parse_query(querystring)# self.qp.FLAG_WILDCARD)
        self.enq.set_query(query)

        matches = self.enq.get_mset(0, 50)
        return matches

