#!/usr/bin/python2

import cards

my_notes = cards.load_all_notes()
by_length = sorted(my_notes,
                   key=lambda n: len(n.front) + len(n.back),
                   reverse=True)
for note in by_length[:100]:
    print note.guid, note.front[:40], note.front[:40]
