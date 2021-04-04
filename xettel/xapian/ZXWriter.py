
import xapian

folder = "/home/ax/docs/20-work/22-know-and-org/22.01-zk"
#ZK = Z.ZettelkastenMMD.from_folder(folder)
DBpath = folder + "/.bokzdb"
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

class ZXapianFrontend:

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
    
    def add_prefixes(self):
        qp.add_prefix("", "")
        qp.add_prefix("", "S")
        for key in attribute_dictionary.keys():
            qp.add_prefix(key, attribute_dictionary[key])

