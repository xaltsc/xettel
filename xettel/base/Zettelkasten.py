
import Zettel as Z
import os
import xapian

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

    def indices(self):
        for z in self:
            yield z.get_uid()

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

    def to_xapian(self, db, indexer):
        new_docs = 0
        updated_docs = 0
        for zettel in self:
            UID = zettel.get_uid_str()
            newhash= zettel.get_hash().encode("utf-8")
            try:
                qp = xapian.QueryParser()
                qp.add_prefix("uid", "Q")
                query = qp.parse_query('uid:'+UID) 
                enq = xapian.Enquire(db)
                enq.set_query(query)
                match = enq.get_mset(0, 1)
                if len(match) < 1:
                    raise xapian.DocNotFoundError()
                olddoc = db.get_document(match[0].docid)
                oldhash = [ x.term for x in olddoc.termlist() if x.term.startswith(b'H') ][0][1:]
                if oldhash != newhash:
                    db.replace_document(u"Q"+UID, zettel.to_xapian(indexer))
                    updated_docs += 1
            except xapian.DocNotFoundError:
                db.add_document(zettel.to_xapian(indexer))
                new_docs += 1
        print("{0} new docs, {1} docs updated".format(new_docs,updated_docs))

    @classmethod
    def from_xapian(cls, db, folder):
        ZK = Zettelkasten()
        ZK.folder = folder

        maxID = db.get_lastdocid()
        for i in range(1, maxID):
            try:
                doc = db.get_document(i)
                ZK.zettels.append(Zettel.from_xapian(ZK, doc))
            except xapian.DocNotFoundError:
                pass
        return ZK
    

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

