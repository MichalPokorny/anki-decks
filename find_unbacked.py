#!/usr/bin/python2

# TODO: Remove notes no longer linked to any UID
# TODO: Import to specific decks

import cards as mod_cards

import os
import csv
import sys

sys.path.append('/usr/share/anki')
import anki
import anki.importing

def main():
    collection_path = '/home/prvak/dropbox/anki/User 1/collection.anki2'
    cwd = os.getcwd()
    collection = anki.Collection(collection_path)
    os.chdir(cwd)


    model = collection.models.byName("Basic (and reversed card) - synchronized with anki-decks")

    my_notes = mod_cards.load_all_notes()
    got_guids = set(note.guid for note in my_notes)

    note_ids = collection.findNotes('mid:' + model['id'])
    existing_uids = set()
    for note_id in note_ids:
        n = collection.getNote(note_id)
        if n.guid not in got_guids:
            print n.guid, n.fields

    collection.close()

if __name__ == '__main__':
    main()
