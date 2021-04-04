import xapian
from zxapian.basic import ZX

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
                    raise xapian.DocNotFoundError()
                olddoc = self.db.get_document(match[0].docid)
                oldhash = [ x.term for x in olddoc.termlist() if x.term.startswith(b'H') ][0][1:]
                if oldhash != newhash:
                    self.db.replace_document(u"Q"+UID, zettel.to_xapian(indexer))
                    updated_docs += 1
            except xapian.DocNotFoundError:
                db.add_document(zettel.to_xapian(indexer))
                new_docs += 1
        print("{0} new docs, {1} docs updated".format(new_docs,updated_docs))

