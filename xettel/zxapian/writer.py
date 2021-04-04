import xapian
from xettel.zxapian.basic import ZX

from xettel.zxapian.reader import ZXReader

class ZXWriter(ZX):

    def __init__(self, folder, ZK):
        self.folder = folder
        self.db = xapian.WritableDatabase(self.folder + '/.xetteldb', xapian.DB_CREATE_OR_OPEN)
        super().__init__(folder, db=self.db)

        self.indexer = xapian.TermGenerator()
        self.indexer.set_stemmer(self.stemmer)
        self.indexer.set_database(self.db)

        self.ZK = ZK

    def zk_to_db(self):
        new_docs = 0
        updated_docs = 0
        for zettel in self.ZK.to_xapian():
            UID = zettel.get_uid_str()
            newhash= zettel.get_hash().encode("utf-8")
            try:
                query = self.qp.parse_query('uid:'+UID) 
                self.enq.set_query(query)
                match = self.enq.get_mset(0, 1)
                if len(match) < 1:
                    raise xapian.DocNotFoundError("no match for uid: {0}".format(UID))
                olddoc = self.db.get_document(match[0].docid)
                oldhash = [ x.term for x in olddoc.termlist() if x.term.startswith(b'H') ][0][1:]
                if oldhash != newhash:
                    self.db.replace_document(u"Q"+UID, zettel.to_xapian(indexer))
                    updated_docs += 1
            except xapian.DocNotFoundError:
                self.db.add_document(zettel.to_xapian(self.indexer))
                new_docs += 1
        print("{0} new docs, {1} docs updated".format(new_docs,updated_docs))

    def delete_in_db(self):
        current_dbzk = ZXReader(self.folder).db_to_zk() 
        count = 0
        for zettel in current_dbzk:
            uid = zettel.get_uid()
            if uid not in self.ZK:
                term = 'Q'+str(uid)
                self.db.delete_document(term)
                count += 1
        print("{0} documents deleted in database".format(count))


