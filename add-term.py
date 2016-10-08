#!/usr/bin/python3

import uuid

print("Term?")
term = input()
print("Definition?")
definition = input()

card_uuid = uuid.uuid1()

with open('/home/prvak/repos/anki-decks/notes/terms.yaml', 'a') as f:
    f.write(("""\t# Added by add-term.py
\t-
\t\tuuid: %(uuid)s
\t\tfront: "%(term)s"
\t\tback: "%(definition)s"
\t\tinclude_reverse: true
""" % {'uuid': card_uuid, 'term': term, 'definition': definition}).replace('\t', ' ' * 8))

print("Term added.")
