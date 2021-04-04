import xapian

class ZX:
  def __init__(self, folder, db=None):
    self.folder = folder
    self.db = db
    if self.db is not None:
      self.stemmer = xapian.Stem("english", "french")
      self.enq = xapian.Enquire(self.db)
      self.qp = xapian.QueryParser()
      

      self.qp.add_prefix("uid", "Q")


