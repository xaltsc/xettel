# readme

NAME: TO FIND

The goal is to build a notmuch-like Zettelkasten filter. The language in which
this will be built is still to determine, but I think we may to code it in
either pyhton, lua or haskell.

To be thorough, the program will be an abstraction layer atop xapian, much
like notmuch is. Its main purposes is to give a way of access to zettels, let it
be by UID, tags, description or internal text (which is wished for by sbbls).

Globally, let call the program `xyz` for instance. We should be issuing the
following commands

`xyz search -- tag:math` lists all math related entries
`xyz tag -analysis +algebra -- gln` tags with algebra remove analysis tags with all entries containing mention of GL_N
`xyz search -- backlink:$UID` list all Zettels linking to the Zettel $UID
`xyz search -- links:$UID` lists all outgoing links from $UID

Much like `notmuch`, some other less useful on a daily basis may be added.

A detail of particular importance is that is it should not the job of `xyz` to
define how zettels exist neither how it should query for metadata or adding
metadata. That is the user's job, although we may on a first phase work with
individual MultiMarkdown files.

In the end, `xyz` should be two things:
  1. A library through which the user defines ways of access
  2. A wrapper around `xapian` that allows for an easy search thorough the
     Zettelkasten.

