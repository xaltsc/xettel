
import xapian

attributes_dict = {
        "abstract": "B",
        "date": "D",
        "filename": "F",
        "hash": "H",
        "jdproject": "JD",
        "tag": "K",
        "tags": "K",
        "backlinks": "LI",
        "links": "LO",
        "filepath": "P",
        "uid": "Q",
        "text": "T",
        "title": "S",
        }

class ZXWriter:

    def __init__(self, folder, ZK):
        self.folder = folder
        self.db = xapian.Database(self.folder + '/.xetteldb')
        self.ZK = ZK

    def dump_to_db(self):
        db = xapian.WritableDatabase(self.folder + '/.xetteldb', xapian.DB_CREATE_OR_OPEN)
        indexer = xapian.TermGenerator()
        stemmer = xapian.Stem("english", "french")
        indexer.set_stemmer(stemmer)
        indexer.set_database(db)

        self.ZK.to_xapian(db, indexer)
