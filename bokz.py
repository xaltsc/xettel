#!/usr/bin/env python

import xapian
import os
import subprocess

DB_PATH="/home/ax/docs/20-work/22-know-and-org/22.01-zk/.bokzdb"

try:
    print("lol")
#    db = xapian.WriteableDatable(DB_PATH, xapian.DB_CREATE_OR_OPEN)

#    indexer = xapian.TermGenerator()

#    for file in 
#        doc = xapian.Document()
#        doc.set_data()
#
#        indexer.set_document(doc)
#        db.add_document(doc)
except Exception as e:
    print("Exception: %s" % str(e), file=sys.stderr)
    sys.exit(1)
